# COSC 520 Assignment 3: Vertex Cover and Graph Coloring

This project compares two vertex-cover algorithms and two greedy graph-coloring orders on undirected, unweighted graphs. All four algorithms are implemented in Python without a graph-algorithm package.

## Setup

Use Python 3.10 or newer. From this directory:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt

The only dependencies are pytest for tests and matplotlib for plots.

## Run

    python -m pytest -q
    python -m scripts.demo
    python -m scripts.demo data/frb/frb30-15-1.mis
    python -m scripts.benchmark --profile quick --prefix my_quick_run
    python -m scripts.benchmark --profile full --prefix my_full_run
    python -m scripts.plot_results --input results/my_full_run_summary.csv --prefix my_full_run

Run commands from the repository root. The demo prints solution sizes and validity for all four methods. The benchmark refuses to overwrite an existing prefix. A full run uses five timed trials per method and graph; --trials and --seed change those settings. Results go to results/ as raw CSV, median summary CSV, and JSON metadata. Plots go to plots/ as PNG and PDF.

The included final files were made with:

    python -m scripts.benchmark --profile full --trials 5 --seed 520 --prefix final
    python -m scripts.plot_results --input results/final_summary.csv --prefix final

To create another deterministic DIMACS graph:

    python -m scripts.generate_graph --vertices 1000 --edges 4000 --seed 520 --output data/example.col

The generator writes an exact edge count and uses a local seeded random number generator. It refuses to overwrite the output. The benchmark creates its synthetic graphs in memory before timing, using the same seed and graph for both methods of each problem.

## Implementations

- src/graph.py stores an edge list and adjacency lists, reads DIMACS files, and generates synthetic graphs.
- src/vertex_cover.py has the basic edge-pair algorithm and the one-endpoint randomized variant. Both return a valid cover.
- src/graph_coloring.py colors vertices in natural order or in Largest First order, which sorts by original degree. Both use the lowest legal color.
- scripts/benchmark.py measures each complete algorithm call. Graph input and result validation are outside the timed interval.
- scripts/plot_results.py plots measured median runtime and solution quality.
- tests/ covers algorithms, input validation, deterministic generation, and benchmark output.

With V vertices and E edges, both cover methods use O(E) time after the graph has been built. Greedy coloring uses O(V+E) time; Largest First adds O(V log V) sorting. The graph representation itself uses O(V+E) space. The report gives the assumptions and details.

## Benchmark data

data/frb/ contains instance 1 from each of four [official BHOSLIB/FRB families](https://rb-bench.github.io/benchmarks/hidden-opt-graph.html): 30-15, 35-17, 40-19, and 45-21. The .mis graphs are for vertex cover; their known minimum cover sizes are 420, 560, 720, and 900. The .clq complement graphs are for coloring; their known chromatic numbers are 30, 35, 40, and 45. Each pair of methods receives the same graph. The included DIMACS text has LF line endings and trimmed header spacing; its edge lists match the official files. The benchmark metadata records each included file's SHA-256 checksum.

The full profile also includes sparse graphs with V = 500, 1,000, 2,500, 5,000, 10,000, and 20,000 and E = 4V, plus denser graphs with V = 200, 400, 800, and 1,200 and about 10% of possible edges. The sparse generator seed is 520+V; the dense seed is 520+2V. No optimum is claimed for these synthetic graphs. Every randomized-cover trial uses seed 520+trial. The same graph is reused for both methods in each comparison. The benchmark includes sorting time in Largest First runtime, which is part of that method.

results/final_raw.csv preserves all individual trials. results/final_summary.csv contains medians and standard deviations. results/final_metadata.json records the platform, Python version, sources, seeds, and checksums. No result is fabricated or inferred for a graph that was not measured.

## Report

The ACM Small source and PDF are in report/. Build locally with:

    cd report
    latexmk -pdf report.tex

The report uses the included final plots. The source and dataset links in it should be checked before submission.
