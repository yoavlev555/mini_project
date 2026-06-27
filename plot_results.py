"""
plot_results.py
===============
Run the streaming spanner on every scenario defined in scenarios.json and
record actual spanner size vs the illustrative paper estimate.

Always writes results/spanner_sizes.csv.
If matplotlib is installed, also writes results/spanner_sizes.png.
"""

from __future__ import annotations

import csv
from pathlib import Path

from scenarios import load_scenarios
from streaming_spanner import StreamingSpanner, theoretical_spanner_bound

RESULTS_DIR = Path("results")
CSV_PATH = RESULTS_DIR / "spanner_sizes.csv"
PNG_PATH = RESULTS_DIR / "spanner_sizes.png"


def collect_rows() -> list[dict]:
    rows = []
    for scenario in load_scenarios():
        n, stream = scenario.build()
        algo = StreamingSpanner(n, scenario.t, seed=scenario.seed)
        spanner = algo.run(stream)
        size = len(spanner)
        bound = theoretical_spanner_bound(n, scenario.t)
        rows.append({
            "name": scenario.name,
            "n": n,
            "t": scenario.t,
            "spanner_size": size,
            "theoretical_bound": bound,
            "ratio": round(size / bound, 3) if bound else 0.0,
        })
    return rows


def write_csv(rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(exist_ok=True)
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "n", "t", "spanner_size", "theoretical_bound", "ratio"]
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

    labels = [r["name"] for r in rows]
    actual = [r["spanner_size"] for r in rows]
    bound = [r["theoretical_bound"] for r in rows]
    x = range(len(labels))

    fig, ax = plt.subplots(figsize=(14, 5))
    width = 0.35
    ax.bar([i - width / 2 for i in x], actual, width, label="actual spanner size")
    ax.bar([i + width / 2 for i in x], bound,  width, label="paper estimate", alpha=0.7)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=40, ha="right", fontsize=8)
    ax.set_ylabel("edge count")
    ax.set_title("Spanner size vs paper estimate (all scenarios)")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(PNG_PATH, dpi=120)
    plt.close()
    print(f"Wrote {PNG_PATH}")


def main() -> None:
    rows = collect_rows()
    write_csv(rows)
    write_png(rows)
    print(f"\n{'scenario':<35} {'n':>5} {'t':>2}  {'actual':>7}  {'estimate':>8}  {'ratio':>5}")
    print("-" * 70)
    for r in rows:
        print(
            f"{r['name']:<35} {r['n']:>5} {r['t']:>2}"
            f"  {r['spanner_size']:>7}  {r['theoretical_bound']:>8}  {r['ratio']:>5.3f}"
        )


if __name__ == "__main__":
    main()