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
    "min_lat": 28.4849,
    "max_lat": 28.6455,
    "min_lon": 77.0731,
    "max_lon": 77.2409,
}


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
def calculate_route(
    start_lat: float = Query(...),
    start_lon: float = Query(...),
    end_lat: float = Query(...),
    end_lon: float = Query(...),
):
    if not is_in_delhi(start_lat, start_lon):
        return {"error": "Start point is outside Delhi boundary."}
    if not is_in_delhi(end_lat, end_lon):
        return {"error": "End point is outside Delhi boundary."}

    t0 = time.perf_counter()
    result = graph.route(start_lat, start_lon, end_lat, end_lon)
    elapsed_ms = (time.perf_counter() - t0) * 1000

    print(f"[DEBUG] Dijkstra execution time: {elapsed_ms:.2f} ms")

    if not result["path"]:
        return {"error": "No path found between the selected points."}
    return result


@app.get("/api/stats")
def graph_stats():
    return {
        "nodes": graph.node_count,
        "edges": graph.edge_count,
    }


@app.get("/api/bounds")
def graph_bounds():
    lats = [c[0] for c in graph.coords.values()]
    lons = [c[1] for c in graph.coords.values()]
    return {
        "min_lat": min(lats),
        "max_lat": max(lats),
        "min_lon": min(lons),
        "max_lon": max(lons),
    }
