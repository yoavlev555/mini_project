"""
demo.py
=======
Runs a suite of experiments to demonstrate the streaming spanner algorithm
on different graph types and stretch parameters.

Usage
-----
    python demo.py
"""

from streaming_spanner import (
    StreamingSpanner,
    verify_spanner,
    verify_spanner_all_pairs,
)

from stream_generators import (
    complete_graph_stream,
    erdos_renyi_stream,
    grid_stream,
    path_stream,
)

FULL_VERIFY_MAX_N = 200


def run_experiment(
    name: str,
    n: int,
    t: int,
    stream: list,
    seed: int = 0,
    full_verify: bool = True,
) -> None:
    """Run one experiment and print formatted results."""
    algo = StreamingSpanner(n, t, seed=seed)
    H = algo.run(stream)
    s = algo.stats()

    edge_valid, max_edge_dist = verify_spanner(H, stream, t)
    edge_status = "PASS" if edge_valid else "FAIL"

    print(f"\n  {name}")
    print(f"    n={n}, t={t}, guaranteed stretch <= {2 * t - 1}, p~{s['p']:.4f}")
    print(f"    stream size       : {s['edges_seen']}")
    print(
        f"    spanner size      : {s['spanner_size']}"
        f"  (tree={s['tree_edges']}, cross={s['cross_edges']},"
        f" dropped={s['dropped_edges']})"
    )
    print(
        f"    paper estimate    : ~{s['theoretical_bound']}"
        f"  (ratio actual/estimate = {s['bound_ratio']})"
    )
    print(
        f"    edge stretch check: {edge_status}"
        f"  (max dist for adjacent pairs = {max_edge_dist})"
    )

    if full_verify and n <= FULL_VERIFY_MAX_N:
        all_valid, max_ratio = verify_spanner_all_pairs(H, stream, n, t)
        all_status = "PASS" if all_valid else "FAIL"
        print(
            f"    all-pairs check   : {all_status}"
            f"  (max stretch ratio = {max_ratio:.3f})"
        )
    elif full_verify:
        print(f"    all-pairs check   : SKIP (n={n} > {FULL_VERIFY_MAX_N})")
    else:
        print("    all-pairs check   : SKIP (disabled)")


def main() -> None:
    print("=" * 64)
    print("  Elkin 2011 - Streaming Spanner Simulation")
    print("  (2t-1)-spanner, one pass, O(1) per edge")
    print("=" * 64)

    # --- Complete graphs ---
    run_experiment("Complete K_15, t=2", 15, 2, complete_graph_stream(15, seed=1))
    run_experiment("Complete K_30, t=2", 30, 2, complete_graph_stream(30, seed=2))
    run_experiment("Complete K_30, t=3", 30, 3, complete_graph_stream(30, seed=3))
    run_experiment("Complete K_50, t=2", 50, 2, complete_graph_stream(50, seed=10))

    # --- Path graphs ---
    run_experiment("Path P_30, t=2", 30, 2, path_stream(30, seed=11))
    run_experiment("Path P_50, t=2", 50, 2, path_stream(50, seed=12))

    # --- Grid graphs ---
    n, s = grid_stream(8, 8, seed=4)
    run_experiment("8x8 grid, t=2", n, 2, s)
    n, s = grid_stream(8, 8, seed=5)
    run_experiment("8x8 grid, t=3", n, 3, s)
    n, s = grid_stream(10, 10, seed=6)
    run_experiment("10x10 grid, t=2", n, 2, s)

    # --- Random graphs ---
    run_experiment(
        "Erdos-Renyi G(100, 500), t=2", 100, 2, erdos_renyi_stream(100, 500, seed=7)
    )
    run_experiment(
        "Erdos-Renyi G(100, 500), t=3", 100, 3, erdos_renyi_stream(100, 500, seed=8)
    )
    run_experiment(
        "Erdos-Renyi G(200, 1000), t=2", 200, 2, erdos_renyi_stream(200, 1000, seed=9)
    )

    print()


if __name__ == "__main__":
    main()
