# Delhi PathFinder

Delhi PathFinder is a FastAPI + Leaflet web app that finds shortest routes in Delhi using a hybrid strategy:

- local in-memory graph + custom Dijkstra for fast routing inside local graph coverage
- OSRM fallback for routes outside local graph coverage or when local routing fails

It is built as a practical DSA project using real OpenStreetMap-derived node/edge data.

## Live Demo

- [https://delhi-pathfinder.onrender.com/](https://delhi-pathfinder.onrender.com/)

## Features

- Custom Dijkstra implementation with priority queue (`heapq`)
- KDTree-based nearest-node lookup for fast graph snapping
- Hybrid routing:
  - prefer local route when both points are inside graph bounds
  - fallback to OSRM when outside bounds or local path is unavailable
- Geocoding by place name using Nominatim
- Interactive frontend map with route drawing and distance display
- Route source visibility (`LOCAL` vs `OSRM`) in UI
- API endpoints for routing, geocoding, stats, and bounds

## Tech Stack

- Backend: Python, FastAPI, Uvicorn, Gunicorn
- Routing/Algorithms: custom Dijkstra, SciPy KDTree
- Data: Pandas + NumPy on OSM-derived CSV graph data
- HTTP client: HTTPX
- Frontend: HTML, CSS, Vanilla JavaScript, Leaflet
- Data preparation: OSMnx (`nodesprep.py`)
- Dependency management: `uv` (with lock file), optional `requirements.txt` for platform deploys

## Project Structure

- `main.py` - FastAPI app, endpoint handlers, local-vs-OSRM decision logic
- `graph_engine.py` - graph loader, bounds logic, KDTree, Dijkstra routing
- `static/index.html` - frontend UI and map behavior
- `static/style.css` - UI styling
- `delhi_nodes.csv` - node list (`osmid`, lat/lon)
- `delhi_edges.csv` - edges with lengths
- `nodesprep.py` - script to regenerate graph CSVs from OSM
- `tests/test_api.py` - API smoke + hybrid-routing tests
- `pyproject.toml` / `uv.lock` - project dependencies
- `requirements.txt` - generated dependency list for non-uv deploy environments

## How Routing Works

1. Validate points are inside Delhi boundary guard.
2. Check whether both points are inside local graph bounds.
3. If inside, run local Dijkstra route first.
4. If local fails or points are outside local bounds, call OSRM:
   - `https://routing.openstreetmap.de/routed-car/route/v1/driving/`
5. Return normalized response with `route_source` (`local` or `osrm`).

## API Endpoints

- `GET /`  
  Serves the frontend.

- `GET /api/geocode?query=<place>`  
  Geocodes a place name within Delhi.

- `GET /api/route?start_lat=...&start_lon=...&end_lat=...&end_lon=...`  
  Returns route path and metadata.

- `GET /api/stats`  
  Returns graph node/edge counts.

- `GET /api/bounds`  
  Returns local graph bounds derived from loaded CSV nodes.

### Example Route Response

```json
{
  "path": [{"lat": 28.61, "lon": 77.20}, {"lat": 28.60, "lon": 77.19}],
  "distance_m": 1523.9,
  "distance_km": 1.524,
  "nodes_traversed": 47,
  "start_node": 123,
  "end_node": 456,
  "route_source": "local"
}
```

## Local Setup (uv)

### Prerequisites

- Python 3.13+ installed
- `uv` installed

### Install

```powershell
uv sync
```

### Run

```powershell
uv run uvicorn main:app --reload
```

Open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/docs`

## Testing

Run all tests:

```powershell
uv run python -m unittest discover -s tests -p "test_*.py" -v
```

Current tests cover:

- root/UI availability
- stats and bounds
- local route success
- outside-Delhi rejection
- OSRM fallback for outside local bounds
- OSRM fallback after local failure
- error handling when both local and OSRM fail

## Regenerating Graph Data

`nodesprep.py` can regenerate CSV graph data from OSMnx.

```powershell
uv run python nodesprep.py
```

This rewrites:

- `delhi_nodes.csv`
- `delhi_edges.csv`

After regenerating, restart the app so bounds and KDTree are rebuilt.

## Render Deployment

You can deploy with either `uv` flow or `requirements.txt` flow.

### Option A: Using uv (preferred if available in environment)

- Build Command: `uv sync --frozen`
- Start Command: `uv run gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`

### Option B: Using requirements.txt (fallback-safe)

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`

## Notes and Limitations

- Local graph coverage depends on current CSV data extent.
- OSRM fallback depends on external network availability and server health.
- Geocoding uses Nominatim and may be rate-limited.
- CSV graph loading is done in-memory on startup; large datasets increase startup time and memory use.

## Future Improvements

- Add caching for geocode and OSRM responses
- Add background refresh for expanded Delhi graph
- Add route alternatives and ETA estimates
- Add CI workflow for tests and lint checks
