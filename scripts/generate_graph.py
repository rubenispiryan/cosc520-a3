"""Write a deterministic synthetic graph in DIMACS format."""

import argparse
from pathlib import Path

from src.graph import random_graph


def main() -> None:
    """Generate a graph from CLI size and seed, and write its DIMACS file."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vertices", type=int, required=True)
    parser.add_argument("--edges", type=int, required=True)
    parser.add_argument("--seed", type=int, default=520)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    graph = random_graph(args.vertices, args.edges, args.seed)
    with args.output.open("x", encoding="ascii") as output:
        output.write(f"c generated with seed {args.seed}\n")
        output.write(f"p edge {graph.vertex_count} {graph.edge_count}\n")
        for u, v in graph.edges:
            output.write(f"e {u + 1} {v + 1}\n")
    print(f"Wrote {args.output}: {graph.vertex_count} vertices, {graph.edge_count} edges")


if __name__ == "__main__":
    main()
