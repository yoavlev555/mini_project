"""
stream_generators.py
====================
Functions that build graph edge sets and return them as a shuffled stream.

In the streaming model, edges arrive in an arbitrary order (any permutation
of the edge set).  All generators here shuffle the edges before returning
them, simulating this adversarial ordering.

Available generators
--------------------
  complete_graph_stream(n)         — complete graph K_n
  erdos_renyi_stream(n, m)         — random graph with m edges
  path_stream(n)                   — simple path 1–2–3–…–n
  grid_stream(rows, cols)          — rows × cols grid (4-connected)
"""

import random
from typing import List, Optional, Set, Tuple


def complete_graph_stream(
    n: int, seed: Optional[int] = None
) -> List[Tuple[int, int]]:
    """
    Return all n(n-1)/2 edges of the complete graph K_n in a random order.

    Good for testing worst-case spanner density, because every pair of
    vertices is adjacent so the algorithm must decide for every possible edge.

    Parameters
    ----------
    n    : number of vertices (IDs 1..n)
    seed : optional random seed
    """
    stream = [(u, v) for u in range(1, n + 1) for v in range(u + 1, n + 1)]
    random.Random(seed).shuffle(stream)
    return stream


def erdos_renyi_stream(
    n: int, m: int, seed: Optional[int] = None
) -> List[Tuple[int, int]]:
    """
    Return m distinct random edges among n vertices in a random order.

    Samples edges uniformly at random (without replacement) to produce a
    random sparse graph G(n, m), then shuffles the edges into stream order.

    Parameters
    ----------
    n    : number of vertices (IDs 1..n)
    m    : number of edges (capped at n(n-1)/2 if too large)
    seed : optional random seed
    """
    rng = random.Random(seed)
    max_edges = n * (n - 1) // 2
    edges: Set[Tuple[int, int]] = set()
    while len(edges) < min(m, max_edges):
        u, v = rng.randint(1, n), rng.randint(1, n)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    stream = list(edges)
    rng.shuffle(stream)
    return stream


def path_stream(
    n: int, seed: Optional[int] = None
) -> List[Tuple[int, int]]:
    """
    Return the n-1 edges of the path graph 1–2–3–…–n in a random order.

    A path is the sparsest connected graph, so almost all edges end up in
    the spanner regardless of t.

    Parameters
    ----------
    n    : number of vertices
    seed : optional random seed
    """
    stream = [(i, i + 1) for i in range(1, n)]
    random.Random(seed).shuffle(stream)
    return stream


def grid_stream(
    rows: int, cols: int, seed: Optional[int] = None
) -> Tuple[int, List[Tuple[int, int]]]:
    """
    Return edges of a rows × cols grid graph (4-connectivity) in random order.

    Vertices are numbered left-to-right, top-to-bottom starting from 1.
    Each interior vertex has degree 4 (up, down, left, right).

    Parameters
    ----------
    rows, cols : grid dimensions
    seed       : optional random seed

    Returns
    -------
    (n, stream) where n = rows * cols
    """
    def vid(r: int, c: int) -> int:
        return r * cols + c + 1

    edges = []
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                edges.append((vid(r, c), vid(r, c + 1)))   # horizontal
            if r + 1 < rows:
                edges.append((vid(r, c), vid(r + 1, c)))   # vertical

    random.Random(seed).shuffle(edges)
    return rows * cols, edges