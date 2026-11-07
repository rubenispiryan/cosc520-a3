"""Two vertex-cover algorithms from COSC 520 Assignment 3."""

import random

from .graph import Graph


def basic_vertex_cover(graph: Graph) -> set[int]:
    """Return a cover by taking both ends of every still-uncovered edge."""
    cover: set[int] = set()
    for u, v in graph.edges:
        if u not in cover and v not in cover:
            cover.add(u)
            cover.add(v)
    return cover


def randomized_vertex_cover(graph: Graph, seed: int = 520) -> set[int]:
    """Return a cover by choosing one random end of each uncovered edge."""
    rng = random.Random(seed)
    cover: set[int] = set()
    for u, v in graph.edges:
        if u not in cover and v not in cover:
            cover.add(u if rng.randrange(2) == 0 else v)
    return cover


def is_vertex_cover(graph: Graph, cover: set[int]) -> bool:
    """Return whether every edge has an endpoint in cover."""
    return all(u in cover or v in cover for u, v in graph.edges)
