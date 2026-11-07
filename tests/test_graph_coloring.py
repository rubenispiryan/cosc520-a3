"""Coloring legality and Largest First ordering tests."""

import pytest

from src.graph import Graph, random_graph
from src.graph_coloring import (
    greedy_coloring, largest_first_coloring, largest_first_order,
    is_valid_coloring, color_count,
)


@pytest.mark.parametrize("graph,expected", [
    (Graph.from_edges(0, []), 0),
    (Graph.from_edges(3, []), 1),
    (Graph.from_edges(4, [(0, 1), (1, 2), (2, 3)]), 2),
    (Graph.from_edges(4, [(0, 1), (0, 2), (0, 3),
                          (1, 2), (1, 3), (2, 3)]), 4),
])
def test_known_color_counts(graph, expected):
    for algorithm in (greedy_coloring, largest_first_coloring):
        colors = algorithm(graph)
        assert is_valid_coloring(graph, colors)
        assert color_count(colors) == expected


def test_largest_first_degree_and_ties():
    graph = Graph.from_edges(5, [(0, 1), (0, 2), (0, 3), (1, 2)])
    assert largest_first_order(graph) == [0, 1, 2, 3, 4]


def test_greedy_uses_lowest_available_color():
    graph = Graph.from_edges(3, [(0, 1), (1, 2)])
    assert greedy_coloring(graph) == [0, 1, 0]


def test_random_graph_colorings_are_valid():
    for seed in range(20):
        graph = random_graph(30, 4 * seed, seed)
        for algorithm in (greedy_coloring, largest_first_coloring):
            assert is_valid_coloring(graph, algorithm(graph))


def test_invalid_coloring_detected():
    graph = Graph.from_edges(2, [(0, 1)])
    assert not is_valid_coloring(graph, [0, 0])
    assert not is_valid_coloring(graph, [0])
