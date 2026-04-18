# PRD: Delhi Route Discovery Engine (DRDE)

## 1. Executive Summary
The Delhi Route Discovery Engine (DRDE) is a high-performance navigation system designed to provide ultra-fast, local-first routing within New Delhi. Unlike generic mapping services, DRDE uses a bespoke Dijkstra-based algorithm optimized for a pre-loaded graph of New Delhi's road network, ensuring minimal latency and complete offline capability for core routes.

## 2. Product Vision
To bypass the bloat of modern mapping suites by providing a lightweight, developer-centric routing engine that demonstrates the power of optimized Data Structures and Algorithms (DSA) in a real-world scenario.

---

## 3. Core Features

### 3.1. High-Performance Routing Engine
- **Custom Dijkstra Implementation**: A from-scratch implementation of Dijkstra's algorithm using a priority queue (min-heap) for $O(E \log V)$ efficiency.
- **Local-First Graph**: Loads road network data from optimized CSVs (`delhi_nodes.csv`, `delhi_edges.csv`) into an in-memory adjacency list.
- **Hybrid Data Fetching**: Internal logic handles the static graph; if a point falls outside the local bounds, the system intelligently queries the Overpass API for real-time supplemental data.

### 3.2. Interactive Geospatial Dashboard
- **Leaflet.js Integration**: A fluid, responsive map interface centered on New Delhi.
- **Dynamic Waypoint Selection**: Users can click directly on the map to set "Point A" (Start) and "Point B" (End).
- **Real-Time Visualization**: Shortest paths are rendered as high-contrast polylines with distance labels and node highlights.

### 3.3. Advanced Analytics
- **Path Statistics**: Displays total distance in meters/kilometers and estimated "logical" travel time.
- **Computational Transparency**: Shows the time taken for the algorithm to compute the path (Success metric < 200ms).

---

## 4. Technical Architecture

### 4.1. Stack
| Component | Technology |
| :--- | :--- |
| **Backend** | Python 3.12 (FastAPI) |
| **Package Manager** | `uv` (Next-gen Python tooling) |
| **Frontend** | Vanilla JS, HTML5, CSS3 (Antigravity DNA) |
| **Mapping Library** | Leaflet.js |
| **Algorithm** | Custom Dijkstra (Graph theory) |
| **Data Format** | Pandas-processed OpenStreetMap GDFs |

### 4.2. API Endpoints
- `GET /calculate-path`: 
    - **Params**: `start_lat`, `start_lon`, `end_lat`, `end_lon`
    - **Response**: List of coordinates (JSON), total distance, and time taken.

---

## 5. UI/UX Vision (Antigravity Aesthetics)
- **Theme**: Sleek Dark Mode with vibrant blue and neon accents.
- **Design Style**: Glassmorphism (frosted glass effects) for the control panel.
- **Animations**: Smooth transitions when pathfinding results are rendered.
- **Typography**: Modern sans-serif (Inter/Outfit) for maximum readability.

---

## 6. Success Metrics
1. **Performance**: Median pathfinding latency < 150ms.
2. **Accuracy**: Path alignment with OSMnx-verified road geometry.
3. **Portability**: Zero-config setup via `uv run`.

---

## 7. Development Roadmap
- [x] Data collection and CSV generation (`nodesprep.py`).
- [x] Basic graph building and pathfinding prototype (`main.py`).
- [ ] **Next Step**: Refactor `main.py` to use a custom Dijkstra instead of NetworkX.
- [ ] **Next Step**: Build the FastAPI wrapper.
- [ ] **Next Step**: Develop the Leaflet.js frontend dashboard.