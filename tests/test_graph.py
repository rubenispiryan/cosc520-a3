"""Input and generator tests."""

import pytest

from src.graph import Graph, random_graph, read_dimacs


def test_graph_with_isolated_vertices(tmp_path):
    path = tmp_path / "small.col"
    path.write_text("c comment\np edge 4 1\ne 1 2\n", encoding="ascii")
    graph = read_dimacs(path)
    assert graph.vertex_count == 4
    assert graph.edges == [(0, 1)]
    assert graph.neighbors == [[1], [0], [], []]


@pytest.mark.parametrize("contents", [
    "e 1 2\n",
    "p edge 3 2\ne 1 2\n",
    "p edge 3 1\ne 1 1\n",
    "p edge 3 2\ne 1 2\ne 2 1\n",
    "p edge 3 1\ne 1 4\n",
])
def test_invalid_dimacs(tmp_path, contents):
    path = tmp_path / "bad.col"
    path.write_text(contents, encoding="ascii")
    with pytest.raises(ValueError):
        read_dimacs(path)


def test_random_graph_is_repeatable_and_simple():
    first = random_graph(100, 200, 52)
    second = random_graph(100, 200, 52)
    assert first.edges == second.edges
    assert len(first.edges) == 200
    assert len(set(first.edges)) == 200
    assert all(u < v for u, v in first.edges)


def test_graph_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        Graph.from_edges(3, [(0, 3)])
    with pytest.raises(ValueError):
        random_graph(3, 4, 520)
