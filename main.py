import time

import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from graph_engine import Graph

app = FastAPI(title="Delhi PathFinder")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = Graph()

app.mount("/static", StaticFiles(directory="static"), name="static")

DELHI_BOUNDS = {
    "min_lat": 28.39,
    "max_lat": 28.89,
    "min_lon": 76.84,
    "max_lon": 77.35,
}
LOCAL_BOUNDS_PAD = 0.005
OSRM_BASE_URL = "https://routing.openstreetmap.de/routed-car/route/v1/driving/"


def is_in_delhi(lat: float, lon: float) -> bool:
    return (
        DELHI_BOUNDS["min_lat"] <= lat <= DELHI_BOUNDS["max_lat"]
        and DELHI_BOUNDS["min_lon"] <= lon <= DELHI_BOUNDS["max_lon"]
    )


async def geocode_place(query: str) -> dict | None:
    search_query = f"{query}, Delhi, India"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": search_query, "format": "json", "limit": 1},
                headers={"User-Agent": "DelhiPathFinder/1.0"},
            )
            resp.raise_for_status()
            data = resp.json()
            if not data:
                return None
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "display_name": data[0].get("display_name", query),
            }
        except Exception:
            return None


async def fetch_osrm_route(
    start_lat: float, start_lon: float, end_lat: float, end_lon: float
) -> dict | None:
    coords = f"{start_lon},{start_lat};{end_lon},{end_lat}"
    url = f"{OSRM_BASE_URL}{coords}"
    params = {"overview": "full", "geometries": "geojson"}

    async with httpx.AsyncClient(timeout=12.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            payload = resp.json()
            routes = payload.get("routes", [])
            if not routes:
                return None
            route = routes[0]
            geometry = route.get("geometry", {})
            points = geometry.get("coordinates", [])
            if not points:
                return None

            return {
                "path": [{"lat": p[1], "lon": p[0]} for p in points],
                "distance_m": round(float(route.get("distance", 0.0)), 2),
                "distance_km": round(float(route.get("distance", 0.0)) / 1000, 3),
                "nodes_traversed": len(points),
                "start_node": None,
                "end_node": None,
                "route_source": "osrm",
            }
        except Exception:
            return None


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


@app.get("/favicon.ico")
def serve_favicon():
    import os

    path = os.path.join("static", "favicon.ico")
    if os.path.exists(path):
        return FileResponse(path, media_type="image/x-icon")
    return Response(status_code=204)


@app.get("/api/geocode")
async def geocode(query: str = Query(...)):
    result = await geocode_place(query)
    if not result:
        return {"error": f"Place '{query}' not found in Delhi."}
    if not is_in_delhi(result["lat"], result["lon"]):
        return {"error": f"Place '{query}' is outside Delhi boundary."}
    return result


@app.get("/api/route")
async def calculate_route(
    start_lat: float = Query(...),
    start_lon: float = Query(...),
    end_lat: float = Query(...),
    end_lon: float = Query(...),
):
    if not is_in_delhi(start_lat, start_lon) or not is_in_delhi(end_lat, end_lon):
        return {"error": "Selected points are outside Delhi boundary."}

    in_local_bounds = graph.is_within_bounds(start_lat, start_lon, LOCAL_BOUNDS_PAD) and (
        graph.is_within_bounds(end_lat, end_lon, LOCAL_BOUNDS_PAD)
    )

    local_result = None
    if in_local_bounds:
        t0 = time.perf_counter()
        local_result = graph.route(start_lat, start_lon, end_lat, end_lon)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        print(f"[DEBUG] Dijkstra execution time: {elapsed_ms:.2f} ms")
        if local_result.get("path"):
            local_result["route_source"] = "local"
            return local_result

    osrm_result = await fetch_osrm_route(start_lat, start_lon, end_lat, end_lon)
    if osrm_result:
        return osrm_result
    if in_local_bounds and local_result:
        return {"error": "No path found between the selected points in local and OSRM routing."}
    return {"error": "No route found for selected points."}


@app.get("/api/stats")
def graph_stats():
    return {
        "nodes": graph.node_count,
        "edges": graph.edge_count,
    }


@app.get("/api/bounds")
def graph_bounds():
    return graph.bounds
