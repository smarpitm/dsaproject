import unittest

from fastapi.testclient import TestClient

from main import app


class ApiSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_root_serves_ui(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers.get("content-type", ""))

    def test_stats_and_bounds(self):
        stats = self.client.get("/api/stats")
        self.assertEqual(stats.status_code, 200)
        payload = stats.json()
        self.assertGreater(payload["nodes"], 0)
        self.assertGreater(payload["edges"], 0)

        bounds = self.client.get("/api/bounds")
        self.assertEqual(bounds.status_code, 200)
        data = bounds.json()
        self.assertLess(data["min_lat"], data["max_lat"])
        self.assertLess(data["min_lon"], data["max_lon"])

    def test_route_rejects_outside_delhi(self):
        resp = self.client.get(
            "/api/route",
            params={
                "start_lat": 12.9716,
                "start_lon": 77.5946,
                "end_lat": 28.6139,
                "end_lon": 77.2090,
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIn("outside Delhi", resp.json()["error"])

    def test_route_success_for_known_points(self):
        resp = self.client.get(
            "/api/route",
            params={
                "start_lat": 28.6139,
                "start_lon": 77.2090,
                "end_lat": 28.5562,
                "end_lon": 77.1000,
            },
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["path"])
        self.assertGreater(data["distance_m"], 0)

    def test_favicon_endpoint_is_safe_without_icon(self):
        resp = self.client.get("/favicon.ico")
        self.assertIn(resp.status_code, (200, 204))


if __name__ == "__main__":
    unittest.main()
