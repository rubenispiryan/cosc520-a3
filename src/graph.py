"""Undirected graphs, DIMACS input, and reproducible synthetic graphs."""

from dataclasses import dataclass
from pathlib import Path
import random


@dataclass
class Graph:
    """An undirected simple graph with vertices numbered 0 through n - 1."""

    vertex_count: int
    edges: list[tuple[int, int]]
    neighbors: list[list[int]]

    @classmethod
    def from_edges(cls, vertex_count: int, edges: list[tuple[int, int]]) -> "Graph":
        """Build a graph from zero-based edges; return a validated graph."""
        if vertex_count < 0:
            raise ValueError("vertex_count must be nonnegative")
        neighbors = [[] for _ in range(vertex_count)]
        unique = set()
        clean_edges = []
        for u, v in edges:
            if not (0 <= u < vertex_count and 0 <= v < vertex_count) or u == v:
                raise ValueError("edge has an invalid endpoint or self-loop")
            edge = (min(u, v), max(u, v))
            if edge in unique:
                raise ValueError("duplicate undirected edge")
            unique.add(edge)
            clean_edges.append(edge)
            neighbors[u].append(v)
            neighbors[v].append(u)
        return cls(vertex_count, clean_edges, neighbors)

    @property
    def edge_count(self) -> int:
        """Return the number of undirected edges."""
        return len(self.edges)


def read_dimacs(path: str | Path) -> Graph:
    """Read a DIMACS edge file; return its graph, including isolated vertices."""
    vertex_count = declared_edges = None
    edges = []
    with Path(path).open(encoding="ascii") as source:
        for line_number, line in enumerate(source, 1):
            parts = line.split()
            if not parts or parts[0] == "c":
                continue
            if parts[0] == "p" and len(parts) == 4 and parts[1] == "edge":
                if vertex_count is not None:
                    raise ValueError(f"line {line_number}: repeated problem line")
                vertex_count, declared_edges = map(int, parts[2:])
            elif parts[0] == "e" and len(parts) == 3 and vertex_count is not None:
                edges.append((int(parts[1]) - 1, int(parts[2]) - 1))
            else:
                raise ValueError(f"line {line_number}: invalid DIMACS line")
    if vertex_count is None or len(edges) != declared_edges:
        raise ValueError("missing problem line or incorrect edge count")
    return Graph.from_edges(vertex_count, edges)


def random_graph(vertex_count: int, edge_count: int, seed: int) -> Graph:
    """Generate exactly edge_count distinct edges using a local seeded generator."""
    possible = vertex_count * (vertex_count - 1) // 2
    if vertex_count < 0 or not 0 <= edge_count <= possible:
        raise ValueError("invalid graph size or edge count")
    rng = random.Random(seed)
    edges = set()
    while len(edges) < edge_count:
        u = rng.randrange(vertex_count)
        v = rng.randrange(vertex_count)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    return Graph.from_edges(vertex_count, sorted(edges))
