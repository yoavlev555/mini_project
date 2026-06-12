"""
demo.py
=======
Runs a suite of experiments to demonstrate the streaming spanner algorithm
on different graph types and stretch parameters.

For each experiment it reports:
  - Graph type, n, t, and the theoretical stretch bound (2t-1)
  - Stream size (number of edges processed)
  - Spanner size broken down into tree edges, cross edges, and dropped edges
  - Stretch verification result (BFS check that dist_H(u,v) ≤ 2t-1)

Usage
-----
    python3 demo.py
"""

from streaming_spanner import StreamingSpanner, verify_spanner
from stream_generators import (
    complete_graph_stream,
    erdos_renyi_stream,
    grid_stream,
    path_stream,
)


def run_experiment(
    name: str,
    n: int,
    t: int,
    stream: list,
    seed: int = 0,
) -> None:
    """Run one experiment and print a formatted results line."""
    algo = StreamingSpanner(n, t, seed=seed)
    H = algo.run(stream)
    s = algo.stats()
    valid, max_d = verify_spanner(H, stream, t)

    status = "PASS ✓" if valid else "FAIL ✗"
    print(f"\n  {name}")
    print(f"    n={n}, t={t}, guaranteed stretch ≤ {2*t-1}, p≈{s['p']:.4f}")
    print(f"    stream size  : {s['edges_seen']}")
    print(f"    spanner size : {s['spanner_size']}"
          f"  (tree={s['tree_edges']}, cross={s['cross_edges']}, dropped={s['dropped_edges']})")
    print(f"    stretch check: {status}"
          f"  (max dist in spanner for adjacent pairs = {max_d})")


def main() -> None:
    print("=" * 64)
    print("  Elkin 2011 – Streaming Spanner Simulation")
    print("  (2t-1)-spanner, one pass, O(1) per edge")
    print("=" * 64)

    # --- Complete graphs ---
    run_experiment("Complete K_15, t=2",  15, 2, complete_graph_stream(15, seed=1))
    run_experiment("Complete K_30, t=2",  30, 2, complete_graph_stream(30, seed=2))
    run_experiment("Complete K_30, t=3",  30, 3, complete_graph_stream(30, seed=3))

    # --- Grid graphs ---
    n, s = grid_stream(8,  8,  seed=4);  run_experiment("8×8 grid, t=2",   n, 2, s)
    n, s = grid_stream(8,  8,  seed=5);  run_experiment("8×8 grid, t=3",   n, 3, s)
    n, s = grid_stream(10, 10, seed=6);  run_experiment("10×10 grid, t=2", n, 2, s)

    # --- Random graphs ---
    run_experiment("Erdős–Rényi G(100, 500), t=2",  100, 2, erdos_renyi_stream(100,  500, seed=7))
    run_experiment("Erdős–Rényi G(100, 500), t=3",  100, 3, erdos_renyi_stream(100,  500, seed=8))
    run_experiment("Erdős–Rényi G(200, 1000), t=2", 200, 2, erdos_renyi_stream(200, 1000, seed=9))

    print()


if __name__ == "__main__":
    main()