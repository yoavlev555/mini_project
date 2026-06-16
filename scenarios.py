"""
scenarios.py
============
Shared experiment scenarios for both `demo.py` and the test suite.

Scenarios are declared once in `scenarios.json` and loaded here into `Scenario`
dataclasses. Each scenario knows how to build its (n, edge-stream) pair from the
appropriate generator in `stream_generators.py`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from stream_generators import (
    complete_graph_stream,
    erdos_renyi_stream,
    grid_stream,
    path_stream,
)

SCENARIOS_PATH = Path(__file__).resolve().parent / "scenarios.json"


@dataclass
class Scenario:
    """One experiment: a graph generator plus its parameters and stretch `t`."""

    name: str
    graph: str            # 'complete' | 'erdos_renyi' | 'grid' | 'path'
    t: int
    seed: int
    params: dict

    def build(self) -> Tuple[int, List[Tuple[int, int]]]:
        """Return (n, edge_stream) for this scenario."""
        g = self.graph
        if g == "complete":
            n = self.params["n"]
            return n, complete_graph_stream(n, seed=self.seed)
        if g == "erdos_renyi":
            n = self.params["n"]
            return n, erdos_renyi_stream(n, self.params["m"], seed=self.seed)
        if g == "path":
            n = self.params["n"]
            return n, path_stream(n, seed=self.seed)
        if g == "grid":
            return grid_stream(self.params["rows"], self.params["cols"], seed=self.seed)
        raise ValueError(f"unknown graph type: {g!r}")


def load_scenarios(path: Path = SCENARIOS_PATH) -> List[Scenario]:
    """Load and parse all scenarios from the shared JSON file."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return [Scenario(**item) for item in raw]
