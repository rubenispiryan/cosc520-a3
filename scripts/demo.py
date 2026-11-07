"""Show all four methods on one DIMACS graph."""

import argparse
from pathlib import Path

from src.graph import read_dimacs
from src.vertex_cover import basic_vertex_cover, randomized_vertex_cover, is_vertex_cover
from src.graph_coloring import greedy_coloring, largest_first_coloring, is_valid_coloring, color_count


def main() -> None:
    """Read one graph, run every algorithm, and print validated result sizes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, nargs="?", default=Path("data/demo.col"))
    parser.add_argument("--seed", type=int, default=520)
    args = parser.parse_args()
    graph = read_dimacs(args.graph)
    print(f"Graph: {graph.vertex_count} vertices, {graph.edge_count} edges")
    for name, cover in (
        ("Basic cover", basic_vertex_cover(graph)),
        ("Randomized cover", randomized_vertex_cover(graph, args.seed)),
    ):
        print(f"{name}: {len(cover)} vertices; valid={is_vertex_cover(graph, cover)}")
    for name, coloring in (
        ("Basic coloring", greedy_coloring(graph)),
        ("Largest First", largest_first_coloring(graph)),
    ):
        print(f"{name}: {color_count(coloring)} colors; valid={is_valid_coloring(graph, coloring)}")


if __name__ == "__main__":
    main()
