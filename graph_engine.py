import heapq
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.spatial import KDTree


class Graph:
    def __init__(
        self, nodes_csv: str = "delhi_nodes.csv", edges_csv: str = "delhi_edges.csv"
    ):
        self.adj: dict[int, list[tuple[int, float]]] = defaultdict(list)
        self.coords: dict[int, tuple[float, float]] = {}
        self._load(nodes_csv, edges_csv)
        self._build_spatial_index()

    def _load(self, nodes_csv: str, edges_csv: str):
        nodes_df = pd.read_csv(nodes_csv, usecols=["osmid", "y", "x"])
        edges_df = pd.read_csv(edges_csv, usecols=["u", "v", "length"])

        for osmid, lat, lon in zip(nodes_df["osmid"], nodes_df["y"], nodes_df["x"]):
            self.coords[int(osmid)] = (float(lat), float(lon))

        for u, v, length in zip(edges_df["u"], edges_df["v"], edges_df["length"]):
            u, v = int(u), int(v)
            w = float(length)
            self.adj[u].append((v, w))
            self.adj[v].append((u, w))

        self.node_count = len(self.coords)
        self.edge_count = len(edges_df)

    def _build_spatial_index(self):
        self._node_ids = np.array(list(self.coords.keys()))
        points = np.array([self.coords[nid] for nid in self._node_ids])
        self._kdtree = KDTree(points)

    def find_nearest_node(self, lat: float, lon: float) -> int:
        _, idx = self._kdtree.query([lat, lon])
        return int(self._node_ids[idx])

    def get_shortest_path(self, start: int, end: int) -> tuple[list[int], float]:
        dist: dict[int, float] = {start: 0.0}
        prev: dict[int, int | None] = {start: None}
        pq: list[tuple[float, int]] = [(0.0, start)]

        while pq:
            d, u = heapq.heappop(pq)
            if u == end:
                break
            if d > dist.get(u, float("inf")):
                continue
            for v, w in self.adj[u]:
                nd = d + w
                if nd < dist.get(v, float("inf")):
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(pq, (nd, v))

        if end not in prev:
            return [], 0.0

        path: list[int] = []
        node: int | None = end
        while node is not None:
            path.append(node)
            node = prev[node]
        path.reverse()

        return path, dist[end]

    def route(
        self, start_lat: float, start_lon: float, end_lat: float, end_lon: float
    ) -> dict:
        start_node = self.find_nearest_node(start_lat, start_lon)
        end_node = self.find_nearest_node(end_lat, end_lon)

        if start_node == end_node:
            return {
                "path": [{"lat": self.coords[start_node][0], "lon": self.coords[start_node][1]}],
                "distance_m": 0,
                "distance_km": 0,
                "nodes_traversed": 1,
                "start_node": start_node,
                "end_node": end_node,
            }

        path, distance = self.get_shortest_path(start_node, end_node)

        coordinates = [
            {"lat": self.coords[nid][0], "lon": self.coords[nid][1]} for nid in path
        ]

        return {
            "path": coordinates,
            "distance_m": round(distance, 2),
            "distance_km": round(distance / 1000, 3),
            "nodes_traversed": len(path),
            "start_node": start_node,
            "end_node": end_node,
        }
