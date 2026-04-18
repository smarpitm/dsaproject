from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from graph_engine import Graph

app = FastAPI(title="Antigravity — New Delhi Navigator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = Graph()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_index():
    return FileResponse("static/index.html")


@app.get("/api/route")
def calculate_route(
    start_lat: float = Query(...),
    start_lon: float = Query(...),
    end_lat: float = Query(...),
    end_lon: float = Query(...),
):
    result = graph.route(start_lat, start_lon, end_lat, end_lon)
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
