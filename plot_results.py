"""
plot_results.py
===============
Run the streaming spanner on complete graphs of increasing size and record
spanner size vs the illustrative paper estimate.

Always writes results/spanner_sizes.csv.
If matplotlib is installed, also writes results/spanner_sizes.png.
"""

from __future__ import annotations

import csv
from pathlib import Path

from streaming_spanner import StreamingSpanner, theoretical_spanner_bound
from stream_generators import complete_graph_stream

RESULTS_DIR = Path("results")
CSV_PATH = RESULTS_DIR / "spanner_sizes.csv"
PNG_PATH = RESULTS_DIR / "spanner_sizes.png"

N_VALUES = [10, 15, 20, 30, 50, 75, 100]
T = 2
ALGO_SEED = 0
STREAM_SEED = 1


def collect_rows() -> list[dict]:
    rows = []
    for n in N_VALUES:
        algo = StreamingSpanner(n, T, seed=ALGO_SEED)
        H = algo.run(complete_graph_stream(n, seed=STREAM_SEED))
        size = len(H)
        bound = theoretical_spanner_bound(n, T)
        rows.append({
            "n": n,
            "t": T,
            "spanner_size": size,
            "theoretical_bound": bound,
            "ratio": round(size / bound, 3) if bound else 0.0,
        })
    return rows


def write_csv(rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["n", "t", "spanner_size", "theoretical_bound", "ratio"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {CSV_PATH}")


def write_png(rows: list[dict]) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Install matplotlib to generate PNG: pip install -r requirements-dev.txt")
        return

    ns = [r["n"] for r in rows]
    actual = [r["spanner_size"] for r in rows]
    bound = [r["theoretical_bound"] for r in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(ns, actual, "o-", label="actual spanner size")
    plt.plot(ns, bound, "s--", label="paper estimate (c=3)")
    plt.xlabel("n (complete graph K_n)")
    plt.ylabel("edge count")
    plt.title(f"Spanner size vs paper estimate (t={T})")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=120)
    plt.close()
    print(f"Wrote {PNG_PATH}")


def main() -> None:
    rows = collect_rows()
    write_csv(rows)
    write_png(rows)
    print("\nn  actual  estimate  ratio")
    for r in rows:
        print(
            f"{r['n']:>3}  {r['spanner_size']:>6}  {r['theoretical_bound']:>8}"
            f"  {r['ratio']:>5.3f}"
        )


if __name__ == "__main__":
    main()
