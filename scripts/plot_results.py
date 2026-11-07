"""Plot measured runtime and solution quality from a benchmark summary CSV."""

import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
COLORS = {
    "Basic cover": "tab:blue",
    "Randomized cover": "tab:orange",
    "Basic coloring": "tab:blue",
    "Largest First": "tab:orange",
}
STYLES = {"FRB": ("o", "-"), "Synthetic sparse": ("s", "--"),
          "Synthetic dense": ("^", ":")}


def save_figure(name: str, prefix: str) -> None:
    """Save the current figure as both PNG and vector PDF under plots/."""
    output = ROOT / "plots"
    output.mkdir(exist_ok=True)
    for extension in ("png", "pdf"):
        plt.savefig(output / f"{prefix}_{name}.{extension}", dpi=180, bbox_inches="tight")
    plt.close()


def runtime_plot(rows: list[dict], problem: str, prefix: str) -> None:
    """Plot measured median elapsed time against edge count for one problem."""
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for method in ("Basic cover", "Randomized cover") if problem == "cover" else ("Basic coloring", "Largest First"):
        for family, (marker, line) in STYLES.items():
            points = sorted(
                (int(row["edges"]), float(row["median_ms"]))
                for row in rows if row["problem"] == problem
                and row["method"] == method and row["family"] == family
            )
            if points:
                x, y = zip(*points)
                ax.plot(x, y, marker=marker, linestyle=line, color=COLORS[method],
                        label=f"{method}, {family}")
    ax.set(xlabel="Number of edges (E)", ylabel="Median runtime (ms)",
           title=f"{'Vertex cover' if problem == 'cover' else 'Graph coloring'} runtime")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    save_figure(f"runtime_{problem}", prefix)


def quality_plot(rows: list[dict], problem: str, prefix: str) -> None:
    """Plot FRB solution size divided by the official optimum for each method."""
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    methods = ("Basic cover", "Randomized cover") if problem == "cover" else ("Basic coloring", "Largest First")
    for method in methods:
        points = sorted(
            (int(row["vertices"]), float(row["median_ratio_to_optimum"]))
            for row in rows if row["problem"] == problem
            and row["family"] == "FRB" and row["method"] == method
        )
        if points:
            x, y = zip(*points)
            ax.plot(x, y, marker="o", color=COLORS[method], label=method)
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1, label="Known optimum")
    ax.set(xlabel="Number of vertices (V)", ylabel="Median solution / known optimum",
           title=f"{'Vertex cover' if problem == 'cover' else 'Graph coloring'} quality on FRB graphs")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    save_figure(f"quality_{problem}", prefix)


def main() -> None:
    """Read one summary CSV and generate four plots."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--prefix", default="final")
    args = parser.parse_args()
    with args.input.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    if not rows:
        parser.error("summary CSV is empty")
    for problem in ("cover", "coloring"):
        runtime_plot(rows, problem, args.prefix)
        quality_plot(rows, problem, args.prefix)
    print(f"Saved eight plot files under {ROOT / 'plots'}")


if __name__ == "__main__":
    main()
