"""Cover correctness and approximation tests."""

from itertools import combinations

import pytest

from src.graph import Graph, random_graph
from src.vertex_cover import basic_vertex_cover, randomized_vertex_cover, is_vertex_cover


def optimum_cover_size(graph):
    """Return the exact minimum cover size for a tiny test graph."""
    vertices = range(graph.vertex_count)
    for size in vertices:
        for choice in combinations(vertices, size):
            if is_vertex_cover(graph, set(choice)):
                return size
    return graph.vertex_count


@pytest.mark.parametrize("edges,n", [
    ([], 0), ([], 1), ([(0, 1)], 2),
    ([(0, 1), (1, 2), (2, 3)], 4),
    ([(0, 1), (1, 2), (2, 0)], 3),
    ([(0, 1), (0, 2), (0, 3)], 5),
    ([(0, 3), (1, 3), (2, 3)], 4),
])
def test_both_covers_are_valid(edges, n):
    graph = Graph.from_edges(n, edges)
    assert is_vertex_cover(graph, basic_vertex_cover(graph))
    assert is_vertex_cover(graph, randomized_vertex_cover(graph, 123))


def test_basic_cover_two_approximation_on_small_graphs():
    for seed in range(25):
        graph = random_graph(7, seed % 11, seed)
        optimum = optimum_cover_size(graph)
        assert len(basic_vertex_cover(graph)) <= 2 * optimum


def test_randomized_cover_seed_is_repeatable():
    graph = random_graph(40, 90, 7)
    assert randomized_vertex_cover(graph, 31) == randomized_vertex_cover(graph, 31)


def test_cover_rejects_uncovered_edge():
    graph = Graph.from_edges(2, [(0, 1)])
    assert not is_vertex_cover(graph, set())
