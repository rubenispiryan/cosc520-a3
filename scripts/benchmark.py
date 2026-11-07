"""Benchmark the four algorithms on BHOSLIB and seeded synthetic graphs."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
from statistics import median, stdev
from time import perf_counter_ns

from src.graph import Graph, random_graph, read_dimacs
from src.vertex_cover import basic_vertex_cover, randomized_vertex_cover, is_vertex_cover
from src.graph_coloring import (
    greedy_coloring, largest_first_coloring, is_valid_coloring, color_count,
)

ROOT = Path(__file__).resolve().parents[1]
RAW_FIELDS = [
    "dataset", "family", "problem", "method", "vertices", "edges", "density",
    "trial", "seed", "elapsed_ns", "result", "valid", "known_optimum", "ratio_to_optimum",
]
SUMMARY_FIELDS = [
    "dataset", "family", "problem", "method", "vertices", "edges", "density",
    "trials", "median_ms", "stdev_ms", "median_result", "best_result",
    "known_optimum", "median_ratio_to_optimum",
]
METHODS = {
    "cover": [
        ("Basic cover", basic_vertex_cover),
        ("Randomized cover", randomized_vertex_cover),
    ],
    "coloring": [
        ("Basic coloring", greedy_coloring),
        ("Largest First", largest_first_coloring),
    ],
}


def datasets(profile: str, seed: int):
    """Yield (name, family, problem, graph, source, optimum) benchmark inputs."""
    families = ["30-15"] if profile == "quick" else ["30-15", "35-17", "40-19", "45-21"]
    for family in families:
        optimum_cover = {"30-15": 420, "35-17": 560, "40-19": 720, "45-21": 900}[family]
        optimum_colors = int(family.split("-")[0])
        for suffix, problem, optimum in (
            ("mis", "cover", optimum_cover),
            ("clq", "coloring", optimum_colors),
        ):
            filename = f"frb{family}-1.{suffix}"
            path = ROOT / "data" / "frb" / filename
            yield filename, "FRB", problem, read_dimacs(path), str(path.relative_to(ROOT)), optimum
    sparse_sizes = [500, 2000] if profile == "quick" else [500, 1000, 2500, 5000, 10000, 20000]
    dense_sizes = [200, 400] if profile == "quick" else [200, 400, 800, 1200]
    for n in sparse_sizes:
        graph = random_graph(n, 4 * n, seed + n)
        for problem in METHODS:
            yield f"sparse_{n}", "Synthetic sparse", problem, graph, f"seed={seed+n}; edges=4V", None
    for n in dense_sizes:
        edges = round(0.1 * n * (n - 1) / 2)
        graph = random_graph(n, edges, seed + 2 * n)
        for problem in METHODS:
            yield f"dense_{n}", "Synthetic dense", problem, graph, f"seed={seed+2*n}; density≈0.1", None


def benchmark_graph(dataset, family, problem, graph: Graph, optimum, trials: int, seed: int):
    """Time each method on one graph; return validated raw and summary rows."""
    rows = []
    density = 2 * graph.edge_count / (graph.vertex_count * (graph.vertex_count - 1)) if graph.vertex_count > 1 else 0
    for trial in range(trials):
        # Rotating the pair reduces systematic first-run effects.
        methods = METHODS[problem][trial % 2:] + METHODS[problem][:trial % 2]
        for method, algorithm in methods:
            run_seed = seed + trial if method == "Randomized cover" else ""
            start = perf_counter_ns()
            output = algorithm(graph, run_seed) if run_seed != "" else algorithm(graph)
            elapsed_ns = perf_counter_ns() - start
            valid = is_vertex_cover(graph, output) if problem == "cover" else is_valid_coloring(graph, output)
            if not valid:
                raise AssertionError(f"{dataset}: {method} produced an invalid result")
            value = len(output) if problem == "cover" else color_count(output)
            ratio = value / optimum if optimum else ""
            rows.append({
                "dataset": dataset, "family": family, "problem": problem,
                "method": method, "vertices": graph.vertex_count, "edges": graph.edge_count,
                "density": round(density, 6), "trial": trial, "seed": run_seed,
                "elapsed_ns": elapsed_ns, "result": value, "valid": valid,
                "known_optimum": optimum or "", "ratio_to_optimum": ratio,
            })
    summaries = []
    for method, _ in METHODS[problem]:
        selected = [row for row in rows if row["method"] == method]
        milliseconds = [row["elapsed_ns"] / 1e6 for row in selected]
        values = [row["result"] for row in selected]
        summaries.append({
            "dataset": dataset, "family": family, "problem": problem,
            "method": method, "vertices": graph.vertex_count, "edges": graph.edge_count,
            "density": round(density, 6), "trials": trials,
            "median_ms": median(milliseconds),
            "stdev_ms": stdev(milliseconds) if trials > 1 else 0,
            "median_result": median(values), "best_result": min(values),
            "known_optimum": optimum or "",
            "median_ratio_to_optimum": median(values) / optimum if optimum else "",
        })
    return rows, summaries


def main() -> None:
    """Parse CLI arguments, run benchmarks, and save non-overwriting CSV files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("quick", "full"), default="quick")
    parser.add_argument("--trials", type=int, default=5)
    parser.add_argument("--seed", type=int, default=520)
    parser.add_argument("--prefix", default="run")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be at least 1")
    if not args.prefix.replace("_", "").replace("-", "").isalnum():
        parser.error("--prefix must use letters, numbers, hyphens, or underscores")
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    paths = [out / f"{args.prefix}_{suffix}" for suffix in ("raw.csv", "summary.csv", "metadata.json")]
    if any(path.exists() for path in paths):
        parser.error("output prefix already exists; choose another --prefix")
    raw, summary, sources = [], [], []
    for name, family, problem, graph, source, optimum in datasets(args.profile, args.seed):
        rows, summaries = benchmark_graph(name, family, problem, graph, optimum, args.trials, args.seed)
        raw.extend(rows)
        summary.extend(summaries)
        source_checksum = hashlib.sha256((ROOT / source).read_bytes()).hexdigest() if family == "FRB" else ""
        sources.append({
            "dataset": name, "problem": problem, "source": source,
            "sha256": source_checksum, "vertices": graph.vertex_count,
            "edges": graph.edge_count, "known_optimum": optimum,
        })
        print(f"{name:20} {problem:8} V={graph.vertex_count:6} E={graph.edge_count:7}")
    for path, fields, rows in ((paths[0], RAW_FIELDS, raw), (paths[1], SUMMARY_FIELDS, summary)):
        with path.open("x", newline="", encoding="utf-8") as output:
            writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
    metadata = {
        "profile": args.profile, "trials": args.trials, "base_seed": args.seed,
        "timer": "time.perf_counter_ns; graph creation and validation excluded",
        "python": platform.python_version(), "platform": platform.platform(),
        "machine": platform.machine(), "datasets": sources,
        "frb_source": "https://rb-bench.github.io/benchmarks/hidden-opt-graph.html",
    }
    with paths[2].open("x", encoding="utf-8") as output:
        json.dump(metadata, output, indent=2)
        output.write("\n")
    print("Saved:", *(str(path.relative_to(ROOT)) for path in paths))


if __name__ == "__main__":
    main()
