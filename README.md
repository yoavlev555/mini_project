# Streaming Spanner — Mini Project

Implementation of the Elkin 2011 streaming (2t−1)-spanner algorithm (Sections 3.1–3.4).

**Authors:** Lior Baumoel & Yoav Levin

---

## Requirements

**Core:** Python 3.7+ standard library only — no dependencies for `streaming_spanner.py`, `demo.py`, `scenarios.py`.

**Plotting & analysis:** install matplotlib and numpy:
```bash
pip install -r requirements-dev.txt
```

**Web UI:** no install needed — just serve the folder statically (see below).

---

## Running

### Demo (batch experiments)

```bash
python demo.py
```

Runs all scenarios defined in `scenarios.json` and prints stretch verification results and spanner sizes.

### Full analysis & plots

```bash
python analyze_results.py
```

Runs 60 scenarios across 8 graph families, evaluates 7 hypotheses, and saves 8 plots to `results/`.

### Basic spanner size plot

```bash
python plot_results.py
```

Writes `results/spanner_sizes.csv` and (if matplotlib is installed) `results/spanner_sizes.png`.

### Interactive web simulator

```bash
python -m http.server 8000
```

Open `http://localhost:8000`. Choose **n**, **t**, and **seed**, then click two vertices to stream an edge and see **tree / cross / drop** decisions in real time. The real `streaming_spanner.py` runs directly in the browser via [Pyodide](https://pyodide.org) — no backend, no second implementation.

The first load downloads Pyodide (~few MB); after that it runs locally. Green solid = tree edge, red dashed = cross edge; dropped edges appear in the log only.

---

## Example Usage

```python
from streaming_spanner import StreamingSpanner, verify_spanner
from stream_generators import complete_graph_stream

n, t = 20, 2
stream = complete_graph_stream(n, seed=42)

algo = StreamingSpanner(n, t, seed=0)
H = algo.run(stream)

print(algo.stats())
# {'n': 20, 't': 2, 'stretch_bound': 3, 'edges_seen': 190,
#  'spanner_size': 90, 'theoretical_bound': 309, 'bound_ratio': 0.291,
#  'tree_edges': 15, 'cross_edges': 75, 'dropped_edges': 100}

valid, max_d = verify_spanner(H, stream, t)
print(f"valid: {valid}, max stretch distance: {max_d}")

# Process edges one by one
algo2 = StreamingSpanner(n, t, seed=0)
for u, v in stream:
    decision = algo2.read_edge(u, v)   # returns 'tree', 'cross', or 'drop'
```

### Stream generators

```python
from stream_generators import (
    complete_graph_stream,   # K_n — all n(n-1)/2 edges
    erdos_renyi_stream,      # G(n, m) — random graph with m edges
    path_stream,             # path graph 1-2-3-...-n
    grid_stream,             # rows × cols 4-connected grid
)

stream = complete_graph_stream(n=20, seed=0)
stream = erdos_renyi_stream(n=100, m=500, seed=0)
n, stream = grid_stream(rows=8, cols=8, seed=0)
```

All generators shuffle edges before returning them, simulating arbitrary stream arrival order.

---

## Files

| File | Description |
|------|-------------|
| `streaming_spanner.py` | `StreamingSpanner` class, `verify_spanner`, `theoretical_spanner_bound` |
| `stream_generators.py` | Graph generators: complete, Erdős–Rényi, grid, path |
| `analyze_results.py` | Full 60-scenario experiment suite — 8 graph families, 7 hypotheses, 8 plots |
| `demo.py` | Batch experiments over `scenarios.json` |
| `scenarios.json` | Experiment scenario definitions |
| `scenarios.py` | `Scenario` dataclass + JSON loader |
| `plot_results.py` | Basic spanner size vs n CSV/plot |
| `index.html`, `app.js`, `styles.css` | In-browser interactive simulator (Pyodide) |
| `requirements-dev.txt` | Optional: matplotlib, numpy |
| `REPORT.md` | Full experimental report with plots and analysis |
| `Article.pdf` | Elkin 2011 (primary reference) |
