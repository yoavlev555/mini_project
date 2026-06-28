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
)

from scenarios import load_scenarios


def run_experiment(
    name: str,
    n: int,
    t: int,
    stream: list,
    seed: int = 0,
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


def main() -> None:
    print("=" * 64)
    print("  Elkin 2011 - Streaming Spanner Simulation")
    print("  (2t-1)-spanner, one pass, O(1) per edge")
    print("=" * 64)

    for scenario in load_scenarios():
        n, stream = scenario.build()
        run_experiment(scenario.name, n, scenario.t, stream, seed=scenario.seed)

    print()


if __name__ == "__main__":
    main()
