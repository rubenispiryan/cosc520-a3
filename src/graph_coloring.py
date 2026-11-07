"""Greedy graph coloring in natural and Largest First vertex order."""

from .graph import Graph


def greedy_coloring(graph: Graph, order: list[int] | None = None) -> list[int]:
    """Assign the lowest legal zero-based color in the supplied vertex order."""
    colors = [-1] * graph.vertex_count
    seen = [0] * graph.vertex_count
    if order is None:
        order = list(range(graph.vertex_count))
    for stamp, vertex in enumerate(order, 1):
        for neighbor in graph.neighbors[vertex]:
            color = colors[neighbor]
            if color >= 0:
                seen[color] = stamp
        color = 0
        while seen[color] == stamp:
            color += 1
        colors[vertex] = color
    return colors


def largest_first_order(graph: Graph) -> list[int]:
    """Return vertices by decreasing original degree, breaking ties by ID."""
    return sorted(range(graph.vertex_count),
                  key=lambda vertex: (-len(graph.neighbors[vertex]), vertex))


def largest_first_coloring(graph: Graph) -> list[int]:
    """Return a greedy coloring after sorting vertices by Largest First."""
    return greedy_coloring(graph, largest_first_order(graph))


def is_valid_coloring(graph: Graph, colors: list[int]) -> bool:
    """Return whether every vertex has a color and every edge has two colors."""
    return (len(colors) == graph.vertex_count
            and all(color >= 0 for color in colors)
            and all(colors[u] != colors[v] for u, v in graph.edges))


def color_count(colors: list[int]) -> int:
    """Return the number of colors used by a coloring."""
    return max(colors, default=-1) + 1
