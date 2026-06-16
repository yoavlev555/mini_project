"""
streaming_spanner.py
====================
Core implementation of Elkin 2011 (Sections 3.1–3.4):

    Elkin, M. 2011. Streaming and Fully Dynamic Centralized Algorithms for
    Constructing and Maintaining Sparse Spanners.
    ACM Trans. Algor. 7, 2, Article 20.

Contains:
  - StreamingSpanner           : the streaming algorithm (Algorithm 1)
  - verify_spanner             : BFS stretch check on adjacent pairs
  - theoretical_spanner_bound  : illustrative paper size estimate
"""

from __future__ import annotations

import math
import random
from collections import defaultdict, deque
from typing import Dict, List, Optional, Set, Tuple


# ============================================================================
# StreamingSpanner — Algorithm 1
# ============================================================================

class StreamingSpanner:
    """
    One-pass streaming algorithm that builds a sparse (2t-1)-spanner.

    Given a stream of edges of an unweighted undirected n-vertex graph,
    processes each edge in O(1) time and outputs a (2t-1)-spanner H.

    HOW IT WORKS
    ------------
    Each vertex v maintains:
      P(v)  — label (integer). Initialized to its unique ID I(v).
              Labels encode two things:
                Level L(P)  = (P-1) // n   — propagation depth (0 to t-1)
                Base  B(P)  = ((P-1) % n)+1 — originating root vertex ID
      T(v)  — tree edges (v adopted a neighbor's label)
      X(v)  — cross edges (v saw a new base value)
      M(v)  — set of base values already seen at v (for deduplication)

    A label P is SELECTED if L(P) < r(base_vertex), where r is a random
    radius drawn per vertex.  Selected means: allowed to propagate one hop.

    On each edge (u, v):
      1. Find x = endpoint with the larger label  (x dominates y)
      2. If P(x) is selected  →  tree edge: y adopts label P(x)+n
      3. Else if B(P(x)) ∉ M(y)  →  cross edge: record base value
      4. Else  →  drop (this adjacency is already covered)

    Output: H = ⋃_v T(v)  ∪  ⋃_v X(v)

    Parameters
    ----------
    n    : number of vertices (IDs 1..n)
    t    : stretch parameter; produces a (2t-1)-spanner
    seed : optional random seed for reproducibility

    Example
    -------
    >>> from stream_generators import complete_graph_stream
    >>> algo = StreamingSpanner(n=20, t=2, seed=0)
    >>> H = algo.run(complete_graph_stream(20, seed=1))
    >>> print(algo.stats())
    """

    def __init__(self, n: int, t: int, seed: Optional[int] = None):
        assert n >= 1 and t >= 1, "n and t must be positive integers"
        self.n = n
        self.t = t

        # p = (log n / n)^(1/t)  — controls the truncated geometric distribution
        self.p: float = (math.log(max(n, 2)) / max(n, 2)) ** (1.0 / t)

        if seed is not None:
            random.seed(seed)

        # Preprocessing: sample a random radius r(v) for every vertex.
        # The distribution is truncated geometric:
        #   P(r = k) = p^k * (1-p)  for k in {0, 1, …, t-2}
        #   P(r = t-1) = p^(t-1)
        self.radius: Dict[int, int] = {v: self._sample_radius() for v in range(1, n + 1)}

        # Per-vertex state — all initialized before the stream starts
        self.label: Dict[int, int]        = {v: v for v in range(1, n + 1)}
        self.T:     Dict[int, Set[Tuple]] = {v: set() for v in range(1, n + 1)}
        self.X:     Dict[int, Set[Tuple]] = {v: set() for v in range(1, n + 1)}
        self.M:     Dict[int, Set[int]]   = {v: set() for v in range(1, n + 1)}

        self._cnt = dict(seen=0, tree=0, cross=0, drop=0)

    # -----------------------------------------------------------------------
    # Label arithmetic
    # -----------------------------------------------------------------------

    def _level(self, P: int) -> int:
        """L(P) = floor((P-1) / n)  — level of label P (0-indexed, max t-1)."""
        return (P - 1) // self.n

    def _base(self, P: int) -> int:
        """B(P) = ((P-1) % n) + 1  — base value of label P, always in {1..n}."""
        return ((P - 1) % self.n) + 1

    def _is_selected(self, P: int) -> bool:
        """True if label P is selected: L(P) < r(base_vertex(P))."""
        return self._level(P) < self.radius[self._base(P)]

    def _dominates(self, u: int, v: int) -> bool:
        """
        True iff P(u) ≻ P(v).
        Order: larger label wins; ties broken by larger vertex ID.
        """
        pu, pv = self.label[u], self.label[v]
        return pu > pv or (pu == pv and u > v)

    # -----------------------------------------------------------------------
    # Radius sampling
    # -----------------------------------------------------------------------

    def _sample_radius(self) -> int:
        """
        Sample from the truncated geometric distribution.
        Flip a biased coin (P(heads)=p) until tails or we hit t-1.
        """
        for k in range(self.t - 1):
            if random.random() >= self.p:   # tails → stop
                return k
        return self.t - 1

    # -----------------------------------------------------------------------
    # Algorithm 1 — Read_Edge
    # -----------------------------------------------------------------------

    def read_edge(self, u: int, v: int) -> str:
        """
        Process one edge (u, v) from the stream.  O(1) per call.

        Returns: 'tree' | 'cross' | 'drop'
        """
        self._cnt['seen'] += 1
        e = (min(u, v), max(u, v))

        x, y = (u, v) if self._dominates(u, v) else (v, u)  # x dominates
        px = self.label[x]

        if self._is_selected(px):           # tree edge branch
            self.label[y] = px + self.n
            self.T[y].add(e)
            self._cnt['tree'] += 1
            return 'tree'

        bx = self._base(px)
        if bx not in self.M[y]:            # cross edge branch
            self.M[y].add(bx)
            self.X[y].add(e)
            self._cnt['cross'] += 1
            return 'cross'

        self._cnt['drop'] += 1             # drop branch
        return 'drop'

    # -----------------------------------------------------------------------
    # Stream / result helpers
    # -----------------------------------------------------------------------

    def run(self, stream: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        """Process the full edge stream and return the spanner edge set."""
        for u, v in stream:
            self.read_edge(u, v)
        return self.spanner()

    def spanner(self) -> Set[Tuple[int, int]]:
        """Return H = ⋃_v T(v)  ∪  ⋃_v X(v)."""
        H: Set[Tuple[int, int]] = set()
        for v in range(1, self.n + 1):
            H |= self.T[v]
            H |= self.X[v]
        return H

    def stats(self) -> dict:
        """Return a summary of algorithm statistics."""
        c = self._cnt
        size = len(self.spanner())
        bound = theoretical_spanner_bound(self.n, self.t)
        return {
            'n':                 self.n,
            't':                 self.t,
            'stretch_bound':     2 * self.t - 1,
            'p':                 round(self.p, 6),
            'edges_seen':        c['seen'],
            'spanner_size':      size,
            'theoretical_bound': bound,
            'bound_ratio':       round(size / bound, 3) if bound else 0.0,
            'tree_edges':        c['tree'],
            'cross_edges':       c['cross'],
            'dropped_edges':     c['drop'],
        }


# ============================================================================
# Theoretical bounds and verification
# ============================================================================

_INF = 10 ** 9


def theoretical_spanner_bound(n: int, t: int) -> int:
    """
    Illustrative whp size estimate from Corollary 3.6 (Elkin 2011):

        O(t * n^(1 + 1/t) * (log n)^(1 - 1/t))

    Uses the bare formula (leading constant 1) since big-O hides the true
    constant. For demo/report comparison only — not a proof certificate.
    """
    log_n = math.log(max(n, 2))
    return max(1, int(t * (n ** (1 + 1 / t)) * (log_n ** (1 - 1 / t))))


def verify_spanner(
    spanner: Set[Tuple[int, int]],
    original_edges: List[Tuple[int, int]],
    t: int,
) -> Tuple[bool, int]:
    """
    Verify the (2t-1)-stretch guarantee of the computed spanner using BFS.

    For every edge (u, v) in the original graph (distance 1 in G), checks
    that dist_H(u, v) ≤ 2t-1 in the spanner H.

    Parameters
    ----------
    spanner        : the computed spanner edge set
    original_edges : all edges of the original graph
    t              : stretch parameter

    Returns
    -------
    (is_valid, max_dist)
      is_valid : True if every edge satisfies the stretch bound
      max_dist : largest spanner distance found over all original edges
    """
    adj: Dict[int, Set[int]] = defaultdict(set)
    for u, v in spanner:
        adj[u].add(v)
        adj[v].add(u)

    def bfs_dist(src: int, dst: int) -> int:
        if src == dst:
            return 0
        visited = {src}
        q: deque = deque([(src, 0)])
        while q:
            node, d = q.popleft()
            for nb in adj[node]:
                if nb == dst:
                    return d + 1
                if nb not in visited:
                    visited.add(nb)
                    q.append((nb, d + 1))
        return _INF  # disconnected

    target = 2 * t - 1
    max_d = 0
    valid = True
    seen: Set[Tuple[int, int]] = set()

    for u, v in original_edges:
        e = (min(u, v), max(u, v))
        if e in seen:
            continue
        seen.add(e)
        d = bfs_dist(u, v)
        if d > max_d:
            max_d = d
        if d > target:
            valid = False

    return valid, max_d