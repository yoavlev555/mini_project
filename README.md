# Streaming Spanner — Mini Project

Implementation of the streaming algorithm for constructing sparse graph spanners
from Sections 3.1–3.4 of:

> Elkin, M. (2011). *Streaming and Fully Dynamic Centralized Algorithms for
> Constructing and Maintaining Sparse Spanners.*
> ACM Trans. Algor. 7(2), Article 20.

---

## Background

### What is a Graph Spanner?

Given an unweighted undirected graph `G = (V, E)`, a **(2t−1)-spanner** is a
subgraph `H ⊆ G` such that for every pair of vertices `u, v`:

```
dist_H(u, v)  ≤  (2t−1) · dist_G(u, v)
```

In other words, H preserves all distances up to a factor of `2t−1`.
The goal is to make H as **sparse** as possible while maintaining this guarantee.

### What is a Streaming Algorithm?

In the **streaming model**, edges of the graph arrive one at a time in an
arbitrary order (like a stream). The algorithm must process each edge
immediately and cannot revisit old edges.

This is useful when the graph is too large to store in memory, or when
edges arrive in real time (e.g., network traffic, social network updates).

---

## Algorithm Summary (Algorithm 1, Elkin 2011)

The algorithm builds a `(2t-1)`-spanner in **one pass** over the edge stream,
using **O(1) worst-case time per edge**.

### Parameters

| Symbol | Meaning |
|--------|---------|
| `n`    | Number of vertices |
| `t`    | Stretch parameter (output is a `(2t−1)`-spanner) |
| `p`    | `(log n / n)^(1/t)` — probability for random radii |

### Preprocessing (before the stream starts)

1. Assign unique IDs `I(v) ∈ {1, …, n}` to all vertices.
2. For each vertex `v`, sample a random **radius** `r(v)` from a truncated geometric distribution:
   - `P(r = k) = p^k · (1−p)` for `k ∈ {0, 1, …, t−2}`
   - `P(r = t−1) = p^(t−1)`
3. Initialize each vertex's **label** `P(v) = I(v)`.

### Label Arithmetic

A label `P` encodes two values:
- **Level**: `L(P) = (P−1) // n` — how many hops the label has propagated
- **Base**: `B(P) = ((P−1) % n) + 1` — the ID of the originating root vertex

A label `P` is **selected** if `L(P) < r(base_vertex(P))` — i.e., it is
allowed to propagate one more hop.

### Per-Edge Processing (`read_edge(u, v)`)

```
1. Let x = endpoint with the larger label  (x "dominates" y)
2. if P(x) is a selected label:
       P(y) ← P(x) + n          ← y adopts x's label (level incremented)
       T(y) ← T(y) ∪ {(u,v)}   ← tree edge
3. else if B(P(x)) ∉ M(y):
       M(y) ← M(y) ∪ {B(P(x))}
       X(y) ← X(y) ∪ {(u,v)}   ← cross edge
4. else:
       drop the edge             ← already covered
```

### Output

`H = ⋃_v T(v)  ∪  ⋃_v X(v)`

### Theoretical Guarantees

| Property | Bound |
|----------|-------|
| Stretch | `2t − 1` |
| Spanner size (expected) | `O(t · n^(1+1/t))` |
| Spanner size (w.h.p.) | `O(t · (log n)^(1−1/t) · n^(1+1/t))` |
| Processing time per edge | `O(1)` worst-case |
| Passes over stream | 1 |
| Space | `O(|H| · log n)` bits |

---

## Code Structure (`streaming_spanner.py`)

### `StreamingSpanner` class

The core algorithm.

```python
algo = StreamingSpanner(n=50, t=2, seed=42)

# Option 1: process the whole stream at once
spanner = algo.run(stream)          # stream = list of (u, v) tuples

# Option 2: process edges one by one
for u, v in stream:
    decision = algo.read_edge(u, v) # returns 'tree', 'cross', or 'drop'

spanner = algo.spanner()            # get the final spanner edge set
print(algo.stats())                 # print summary statistics
```

### Stream Generators

Four graph types for experimentation:

```python
from streaming_spanner import (
    complete_graph_stream,  # K_n — all n(n-1)/2 edges
    erdos_renyi_stream,     # G(n, m) — random graph with m edges
    path_stream,            # path graph 1-2-3-...-n
    grid_stream,            # rows × cols grid graph
)

# Examples
stream = complete_graph_stream(n=20, seed=0)
stream = erdos_renyi_stream(n=100, m=500, seed=0)
n, stream = grid_stream(rows=8, cols=8, seed=0)
```

All generators return edges in a **random order** (simulating the streaming
model where edges arrive in an arbitrary permutation).

### `verify_spanner`

**Edge check** (`verify_spanner`): for every edge in the original graph, verifies
`dist_H(u, v) <= 2t-1`. By the triangle inequality this is sufficient to
guarantee the `(2t-1)`-stretch for *all* vertex pairs.

```python
from streaming_spanner import verify_spanner

is_valid, max_dist = verify_spanner(H, stream, t)
```

### `theoretical_spanner_bound`

Returns an illustrative paper size estimate (bare formula, leading constant 1)
for comparing actual spanner size to Corollary 3.6 — not a proof certificate.

```python
from streaming_spanner import theoretical_spanner_bound

estimate = theoretical_spanner_bound(n=100, t=2)
```

---

## Running the Demo

```bash
python demo.py
```

Expected output (results are randomized, but all checks should PASS):

```
================================================================
  Elkin 2011 - Streaming Spanner Simulation
  (2t-1)-spanner, one pass, O(1) per edge
================================================================

  Complete K_15, t=2
    n=15, t=2, guaranteed stretch <= 3, p~0.4249
    stream size       : 105
    spanner size      : 55  (tree=12, cross=43, dropped=50)
    paper estimate    : ~191  (ratio actual/estimate = 0.288)
    edge stretch check: PASS  (max dist for adjacent pairs = 2)
  ...
```

### Plotting spanner size vs n

```bash
python plot_results.py
```

Writes `results/spanner_sizes.csv`. If matplotlib is installed
(`pip install -r requirements-dev.txt`), also writes `results/spanner_sizes.png`.

---

## Example Usage

```python
from streaming_spanner import StreamingSpanner, complete_graph_stream, verify_spanner

# Build a 3-spanner of K_20
n, t = 20, 2
stream = complete_graph_stream(n, seed=42)

algo = StreamingSpanner(n, t, seed=0)
H = algo.run(stream)

print(algo.stats())
# {'n': 20, 't': 2, 'stretch_bound': 3, 'p': 0.386...,
#  'edges_seen': 190, 'spanner_size': 87, 'tree_edges': 16,
#  'cross_edges': 71, 'dropped_edges': 103}

valid, max_d = verify_spanner(H, stream, t)
print(f"Edge check: {valid}, max stretch distance: {max_d}")
```

---

## Files

| File | Description |
|------|-------------|
| `streaming_spanner.py` | `StreamingSpanner` class + verification helpers |
| `stream_generators.py` | Graph generators: complete, Erdős–Rényi, grid, path |
| `demo.py` | Runs experiments across graph types — entry point |
| `plot_results.py` | CSV/plot of spanner size vs n on complete graphs |
| `requirements-dev.txt` | Optional matplotlib for plotting |
| `Arcticle.pdf` | The original paper (Elkin 2011) |
| `README.md` | This file |

Local-only files (gitignored, not in the repo): `FUTURE_WORK.md` optional
backlog and `.cursor/skills/` agent skills.

---

## Requirements

**Core:** Python 3.7+ standard library only (`demo.py`, `streaming_spanner.py`).

**Optional plotting:** `pip install -r requirements-dev.txt` then `python plot_results.py`.