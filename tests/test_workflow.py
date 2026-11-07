"""One small integration test for the benchmark results."""

from scripts.benchmark import benchmark_graph
from src.graph import Graph


def test_benchmark_rows_are_complete_and_valid():
    graph = Graph.from_edges(4, [(0, 1), (1, 2), (2, 3)])
    for problem in ("cover", "coloring"):
        raw, summary = benchmark_graph("tiny", "test", problem, graph, None, 3, 520)
        assert len(raw) == 6
        assert len(summary) == 2
        assert all(row["valid"] for row in raw)
        assert all(row["trials"] == 3 for row in summary)
