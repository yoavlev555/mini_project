# Experimental Analysis: Elkin 2011 Streaming $(2t-1)$-Spanner Algorithm

**Course:** Mini Project - Streaming Spanner Algorithm\
**Authors:** Lior Baumoel & Yoav Levin  
**Date:** June 2026  

---

## Abstract

This report presents a comprehensive experimental evaluation of the one-pass streaming spanner algorithm introduced by Elkin (2011) \[1\]. The algorithm processes an unweighted graph edge stream in $O(1)$ time per edge and produces a **$(2t-1)$-spanner** — a sparse subgraph that preserves all pairwise distances up to a multiplicative factor of $2t-1$.

We designed **7 testable hypotheses** directly grounded in the paper's theoretical claims, ran **60 scenarios** spanning 8 graph families (complete, Erdős–Rényi, grid, path, cycle, star, random tree, tight-bound ER), and validated results against Theorem 3.2 and Corollary 3.6 of \[1\]. All 7 hypotheses were confirmed. A notable finding that contradicts naive intuition — **cross edges dominate the spanner structure (~86%)** — is explained analytically through the algorithm's radius distribution (Section 3.2 of \[1\]).

---

## Table of Contents

1. [Algorithm Overview](#1-algorithm-overview)
2. [Theoretical Predictions](#2-theoretical-predictions)
3. [Hypotheses](#3-hypotheses)
4. [Experimental Setup](#4-experimental-setup)
5. [Results by Hypothesis](#5-results-by-hypothesis)
6. [Full Results Table](#6-full-results-table)
7. [Analysis & Conclusions](#7-analysis--conclusions)
8. [Bibliography](#8-bibliography)

---

## 1. Algorithm Overview

The algorithm is defined in Section 3.1–3.2 of \[1\] (Algorithm 1). It processes a stream of edges of an $n$-vertex unweighted undirected graph in a single pass and outputs a $(2t-1)$-spanner $H$.

### Core Data Structures (per vertex $v$)

| Symbol | Meaning |
|---|---|
| $P(v)$ | Label (integer). Initially $P(v) = v$. Encodes **level** $L(P) = \lfloor(P-1)/n\rfloor$ and **base** $B(P) = ((P-1) \bmod n)+1$ |
| $r(v)$ | Random radius, sampled from a truncated geometric distribution with parameter $p = (\log n / n)^{1/t}$ |
| $T(v)$ | Set of **tree edges** incident to $v$ |
| $X(v)$ | Set of **cross edges** incident to $v$ |
| $M(v)$ | Set of base values already seen at $v$ (deduplication) |

### Edge Processing Rule (Algorithm 1, Section 3.2 of \[1\])

On each edge $(u, v)$, let $x$ = vertex with the larger label ($x$ *dominates* $y$):

```
1. If P(x) is selected  [L(P(x)) < r(base(P(x)))]
       → TREE EDGE: y adopts label P(x)+n; add (u,v) to T(y)
2. Else if B(P(x)) ∉ M(y)
       → CROSS EDGE: M(y) ← M(y) ∪ {B(P(x))}; add (u,v) to X(y)
3. Else
       → DROP (edge is redundant, already covered)
```

The output spanner is $H = \bigcup_v T(v) \cup \bigcup_v X(v)$.

### Key Properties

- **One-pass streaming**: each edge is processed exactly once \[1, Section 3.1\]
- **$O(1)$ per edge**: all operations are constant time \[1, Section 3.3\]
- **Stretch guarantee**: $\text{dist}_H(u,v) \leq 2t-1$ for all $(u,v) \in G$ \[1, Theorem 3.2\]
- **Size bound**: $|H| = O\!\left(t \cdot n^{1+1/t} \cdot (\log n)^{1-1/t}\right)$ with high probability \[1, Corollary 3.6\]

---

## 2. Theoretical Predictions

The following bounds from \[1\] inform all our hypotheses.

### Theorem 3.2 — Stretch Guarantee \[1\]

> For every edge $(u, v) \in G$, the spanner $H$ produced by Algorithm 1 satisfies $\text{dist}_H(u, v) \leq 2t-1$.

This is the core correctness theorem. It follows from the label-propagation invariant: if a vertex $y$ has not adopted the label of its neighbor $x$'s root, then a short path (of at most $2t-1$ hops) via previously propagated labels must already exist in $H$.

### Corollary 3.6 — Size Bound \[1\]

> With high probability:
> $$|H| = O\!\left(t \cdot n^{1+1/t} \cdot (\log n)^{1-1/t}\right)$$

Consequences by $t$ value:

| $t$ | Stretch bound $(2t-1)$ | Expected spanner size | Lower bound \[2,3\] |
|---|---|---|---|
| 2 | 3 | $O\!\left(n^{3/2} \cdot \sqrt{\log n}\right)$ | $\Omega(n^{3/2})$ |
| 3 | 5 | $O\!\left(n^{4/3} \cdot (\log n)^{2/3}\right)$ | $\Omega(n^{4/3})$ |
| 4 | 7 | $O\!\left(n^{5/4} \cdot (\log n)^{3/4}\right)$ | $\Omega(n^{5/4})$ |
| $t \to \infty$ | $\to \infty$ | $\to O(n \log n)$ | $\Omega(n)$ |

The gap between upper and lower bound is only the $\log$ factor — this algorithm is **near-optimal in sparsity**.

### Radius Distribution (Section 3.2 of \[1\])

Each vertex samples radius $r(v)$ from a truncated geometric distribution:

$$P(r = k) = p^k \cdot (1-p) \quad \text{for } k \in \{0, 1, \ldots, t-2\}, \qquad P(r = t-1) = p^{t-1}$$

where

$$p = \left(\frac{\log n}{n}\right)^{1/t}$$

For $t=2$ and $n=100$: $p \approx 0.214$, so $P(r=0) \approx 0.786$ — roughly **78% of vertices** have radius 0 and can never propagate tree edges. This has a major practical consequence (see H7).

---

## 3. Hypotheses

Each hypothesis is derived directly from a specific claim in \[1\].

| ID | Hypothesis | Article Source |
|---|---|---|
| **H1** | Every spanner satisfies $(2t-1)$-stretch for all original edges | \[1\] Theorem 3.2 |
| **H2** | Spanner size scales as $O(n^{3/2})$ for $t=2$ | \[1\] Corollary 3.6 |
| **H3** | Larger $t$ $\Rightarrow$ fewer edges in the spanner, larger stretch bound | \[1\] Corollary 3.6 |
| **H4** | Denser graphs compress more (lower $\lvert H \rvert / \lvert E \rvert$ ratio) | \[1\] Section 3.4 |
| **H5** | Sparse / bridge graphs are near-lossless (ratio $\approx 1.0$) | \[1\] Section 1 |
| **H6** | Actual spanner size stays well below the illustrative bound | \[1\] Corollary 3.6 |
| **H7** | Cross edges dominate the spanner in dense graphs (only $\approx p$ fraction of vertices have $r \geq 1$) | \[1\] Section 3.2 |

---

## 4. Experimental Setup

### Graph Families

| Family | Description | Sizes tested |
|---|---|---|
| Complete $K_n$ | All $n(n-1)/2$ edges | $n \in \{10, 20, 30, 50, 75, 100, 150, 200\}$ |
| Erdős–Rényi $G(n,m)$ | $m$ random edges among $n$ vertices | $n=100$, $m \in \{150, 300, 500, 800, 1200, 2000\}$ |
| Grid $r \times c$ | 4-connected rectangular grid | $5{\times}5$, $8{\times}8$, $10{\times}10$, $15{\times}15$ |
| Path $P_n$ | Linear chain $1{-}2{-}{\cdots}{-}n$ | $n \in \{20, 50, 100\}$ |
| Cycle $C_n$ | $n$-cycle | $n \in \{20, 50, 100\}$ |
| Star $S_n$ | Hub vertex $+$ $n-1$ leaves | $n \in \{20, 50, 100\}$ |
| Random Tree $T_n$ | Random Prüfer-style tree | $n \in \{20, 50, 100\}$ |
| Dense ER | ER with $p=0.5$ ($\approx n^2/4$ edges) | $n \in \{30, 50, 75, 100\}$ |
| Tight-bound ER | Sparse ER chosen to push stretch close to $2t-1$ | $n \in \{30, 50\}$, $t \in \{3, 4\}$ |

### Stretch Parameters Tested

$t \in \{2, 3, 4\}$, giving stretch bounds 3-spanner, 5-spanner, and 7-spanner respectively.

### Metrics Collected per Scenario

| Metric | Definition |
|---|---|
| $\lvert H \rvert$ (spanner_size) | Number of edges in the spanner |
| $\lvert E \rvert$ (original_m) | Number of edges in the original graph |
| compression | $\lvert H \rvert / \lvert E \rvert$ |
| theoretical_bound | $t \cdot n^{1+1/t} \cdot (\log n)^{1-1/t}$ (Corollary 3.6 with constant 1) |
| bound_ratio | $\lvert H \rvert$ / theoretical_bound |
| stretch_valid | True if $\text{dist}_H(u,v) \leq 2t-1$ for all $(u,v) \in G$ |
| max_dist | Largest spanner distance found for any adjacent pair |
| tree_edges | Edges from the tree-propagation branch |
| cross_edges | Edges from the cross-edge branch |

**Total: 60 scenarios** across 8 graph families, $t \in \{2,3,4\}$.

---

## 5. Results by Hypothesis

### H1 — Stretch Correctness

> **Prediction (Theorem 3.2, \[1\]):** Every spanner satisfies $(2t-1)$-stretch for all original edges.
> **Result: ✓ CONFIRMED** — 60/60 scenarios passed, 0 failures.

![Stretch Correctness — all scenarios](results/analysis_H1_stretch_distribution.png)

The figure shows every individual scenario as a dot. **Shape and colour encode the stretch parameter $t$** (circle = $t=2$, square = $t=3$, triangle = $t=4$). The x-axis groups scenarios by graph family; the y-axis shows the maximum spanner distance observed for any adjacent pair. Dashed lines mark the $(2t-1)$ bounds; coloured bands show the allowed stretch region per $t$.

#### Why does the observed max distance stay at 3 even for $t=3$ and $t=4$ on dense graphs?

The bound $2t-1$ is a **worst-case upper guarantee**, not a tight prediction. On dense graphs, the spanner retains enough connectivity that no adjacent pair needs more than 3 hops. The effect of a larger $t$ is visible in the **shift of the distance distribution** — more pairs move to distance 3 — but the bound of 5 or 7 is never needed on dense inputs:

| $K_{100}$, $t$ | $\lvert H \rvert$ | Pairs at dist 1 | Pairs at dist 2 | Pairs at dist 3 | Max dist | Bound |
|---|---|---|---|---|---|---|
| $t=2$ | 1,129 | 1,129 | 3,781 | 40 | 3 | **3** |
| $t=3$ | 951 | 951 | 3,815 | 184 | 3 | **5** |
| $t=4$ | 695 | 695 | 3,612 | 643 | 3 | **7** |

#### The bound is real — tight-bound scenarios

To show the bound is not merely conservative, we searched for sparse ER configurations that push observed stretch close to the theoretical ceiling:

| Scenario | $n$ | $m$ | $t$ | Max dist observed | Bound $2t-1$ | Valid |
|---|---|---|---|---|---|---|
| ER $n=30$, $m=60$ | 30 | 60 | 3 | **4** | 5 | ✓ |
| ER $n=50$, $m=75$ | 50 | 75 | 3 | **5** | 5 | ✓ |
| ER $n=30$, $m=45$ | 30 | 45 | 4 | **5** | 7 | ✓ |
| ER $n=50$, $m=100$ | 50 | 100 | 4 | **6** | 7 | ✓ |

The scenario $n=50$, $m=75$, $t=3$ achieves max distance exactly **5 = 2(3)−1**, hitting the bound precisely. These cases confirm the guarantee is sharp — the margin seen on dense graphs is a property of graph density, not looseness in the algorithm.

**Per-family pass/fail summary:**

| Graph family | Scenarios | Achieved max dist | Bound $(2t-1)$ | Pass rate |
|---|---|---|---|---|
| Complete $K_n$ | 14 | 3 | 3 / 5 / 7 | 14/14 ✓ |
| Path $P_n$ | 3 | 1 | 3 | 3/3 ✓ |
| Cycle $C_n$ | 3 | 1 | 3 | 3/3 ✓ |
| Star $S_n$ | 3 | 1 | 3 | 3/3 ✓ |
| Random Tree $T_n$ | 3 | 1 | 3 | 3/3 ✓ |
| Grid $r{\times}c$ | 8 | 3 | 3 / 5 | 8/8 ✓ |
| Erdős–Rényi | 8 | 3 | 3 / 5 | 8/8 ✓ |
| Dense ER | 4 | 3 | 3 | 4/4 ✓ |
| Tight-bound ER | 4 | **5–6** | 5 / 7 | 4/4 ✓ |

All 60 scenarios remain within the $(2t-1)$ bound, confirming Theorem 3.2 of \[1\]. The stretch bound is order-independent: edges were shuffled uniformly at random before each run, confirming \[1\] Section 3.1.

---

### H2 — Sub-quadratic Size Scaling

> **Prediction (Corollary 3.6, \[1\]):** For complete graphs $K_n$ with $t=2$, spanner size grows as $O(n^{3/2})$.
> **Result: ✓ CONFIRMED** — log-log slope = **1.663** (expected $\approx 1.5$).

![Size Scaling Log-Log](results/analysis_H2_scaling_loglog.png)

| $n$ | $\lvert K_n \rvert$ | $\lvert H \rvert$ | Compression | Paper bound |
|---|---|---|---|---|
| 10 | 45 | 30 | 0.667 | 95 |
| 20 | 190 | 68 | 0.358 | 309 |
| 30 | 435 | 180 | 0.414 | 606 |
| 50 | 1,225 | 585 | 0.478 | 1,398 |
| 75 | 2,775 | 821 | 0.296 | 2,699 |
| 100 | 4,950 | 1,126 | 0.227 | 4,291 |
| 150 | 11,175 | 2,378 | 0.213 | 8,224 |
| 200 | 19,900 | 4,201 | 0.211 | 13,020 |

The fitted slope of **1.663** slightly exceeds the nominal 1.5. This is expected: Corollary 3.6 predicts $O(n^{3/2} \cdot \sqrt{\log n})$, and the $\sqrt{\log n}$ factor contributes a small positive offset to the slope for finite $n$. As $n \to \infty$ the log correction diminishes and the slope converges to 1.5.

---

### H3 — $t$ Trade-off: Size vs. Stretch

> **Prediction (Corollary 3.6, \[1\]):** Larger $t$ produces sparser spanners with exponent $1+1/t$, at the cost of a larger stretch bound $2t-1$.
> **Result: ✓ CONFIRMED** — $|H|$ strictly decreases as $t$ increases for both $K_{50}$ and $K_{100}$.

![t Comparison](results/analysis_H3_t_comparison.png)

#### $K_{50}$ (1,225 edges)

| $t$ | Stretch bound | $\lvert H \rvert$ | Compression | Reduction vs $t=2$ |
|---|---|---|---|---|
| 2 | 3 | 450 | 36.7% | — |
| 3 | 5 | 243 | 19.8% | $-46\%$ |
| 4 | 7 | 219 | 17.9% | $-51\%$ |

#### $K_{100}$ (4,950 edges)

| $t$ | Stretch bound | $\lvert H \rvert$ | Compression | Reduction vs $t=2$ |
|---|---|---|---|---|
| 2 | 3 | 1,129 | 22.8% | — |
| 3 | 5 | 951 | 19.2% | $-16\%$ |
| 4 | 7 | 695 | 14.0% | $-38\%$ |

The $t=2\to3$ jump yields the largest relative improvement for $K_{50}$ ($-46\%$). For $K_{100}$ however, the $t=3\to4$ step is larger ($-27\%$ vs $-16\%$), because with more vertices the radius distribution creates more differentiation between levels. In both cases the marginal benefit of increasing $t$ diminishes overall, consistent with the diminishing gap between the exponents $1+1/t$ as $t$ grows.

---

### H4 — Dense Graphs Compress More

> **Prediction (\[1\] Section 3.4):** The spanner size is bounded by $O(n^{1+1/t})$, independent of $|E|$; hence denser graphs achieve a lower compression ratio.
> **Result: ✓ CONFIRMED** — ratio drops monotonically from 1.0 ($m=150$) to 0.49 ($m=2000$).

![Compression vs Density](results/analysis_H4_compression_vs_density.png)

#### Erdős–Rényi $n=100$, $t=2$

| Original edges $m$ | Spanner $\lvert H \rvert$ | Ratio $\lvert H \rvert / m$ |
|---|---|---|
| 150 | 150 | 1.000 |
| 300 | 294 | 0.980 |
| 500 | 476 | 0.952 |
| 800 | 688 | 0.860 |
| 1,200 | 858 | 0.715 |
| 2,000 | 978 | 0.489 |

The spanner size saturates around $\approx 1{,}000$ edges as $m$ grows, while $\lvert E \rvert$ keeps increasing. This is a direct demonstration of the $O(n^{3/2})$ ceiling from Corollary 3.6 of \[1\]: the bound depends only on $n$, not on $\lvert E \rvert$. The algorithm automatically stops adding edges once the spanner budget is spent — a key advantage of the streaming model.

---

### H5 — Sparse / Bridge Graphs Are Near-Lossless

> **Prediction (\[1\] Section 1):** Any valid $(2t-1)$-spanner must contain every bridge of $G$; therefore tree-structured graphs cannot be compressed.
> **Result: ✓ CONFIRMED** — all sparse graph families show compression ratio $= 1.000$.

![Sparse Compression](results/analysis_H5_sparse_compression.png)

| Graph type | $n=20$ ratio | $n=50$ ratio | $n=100$ ratio |
|---|---|---|---|
| Path | 1.000 | 1.000 | 1.000 |
| Cycle | 1.000 | 1.000 | 1.000 |
| Star | 1.000 | 1.000 | 1.000 |
| Random Tree | 1.000 | 1.000 | 1.000 |

Every edge in these graphs is a bridge or part of a unique cycle. Removing any such edge would give $\text{dist}_H(u,v) = \infty > 2t-1$, violating the stretch guarantee. Note the max distance of **1** for all sparse families — every adjacent pair is directly connected in $H$, far better than the $2t-1=3$ worst-case bound.

---

### H6 — Actual Size Well Below the Theoretical Bound

> **Prediction (Corollary 3.6, \[1\]):** The formula $t \cdot n^{1+1/t} \cdot (\log n)^{1-1/t}$ uses a big-$O$ constant $< 1$; actual sizes should lie comfortably below it.
> **Result: ✓ CONFIRMED** — 60/60 scenarios (100%) are below the bound.

![Actual vs Bound](results/analysis_H6_actual_vs_bound.png)

| Scenario group | Avg ratio | Min ratio | Max ratio |
|---|---|---|---|
| Dense ER | 0.250 | 0.218 | 0.271 |
| ER varying density | 0.141 | 0.035 | 0.228 |
| Grid | 0.052 | 0.026 | 0.087 |
| Complete $K_n$ (scaling) | 0.304 | 0.220 | 0.418 |
| Sparse graphs | 0.040 | 0.023 | 0.065 |
| $t$ comparison | 0.222 | 0.148 | 0.343 |
| Tight-bound ER | 0.067 | 0.052 | 0.090 |
| Variance ($K_{50}$ repeated) | 0.296 | 0.275 | 0.343 |

Actual spanners are **2.4× to 43× smaller** than the illustrative bound. Corollary 3.6 is a *worst-case with-high-probability* upper bound; the hidden constant in the $O(\cdot)$ notation is well below 1.

---

### H7 — Cross Edges Dominate the Spanner

> **Prediction (\[1\] Section 3.2):** With $p = (\log n / n)^{1/t} \ll 1$, most vertices sample $r=0$ and can never generate tree edges; cross edges carry the bulk of the spanner.
> **Result: ✓ CONFIRMED** — average cross edge fraction = **85.8%** across all complete and dense ER graphs.

![Tree vs Cross Breakdown](results/analysis_H7_tree_cross_breakdown.png)

| Graph | Tree edges | Cross edges | Cross % |
|---|---|---|---|
| $K_{10}$ | 9 | 21 | 70.0% |
| $K_{20}$ | 19 | 49 | 72.1% |
| $K_{30}$ | 22 | 158 | 87.8% |
| $K_{50}$ | 37 | 548 | 93.7% |
| $K_{75}$ | 71 | 750 | 91.4% |
| $K_{100}$ | 98 | 1,028 | 91.3% |
| $K_{150}$ | 148 | 2,230 | 93.8% |
| $K_{200}$ | 187 | 4,014 | 95.5% |

**Why cross edges dominate — the radius sparsity argument:**

For $t=2$, the radius parameter is $p = \sqrt{\log n / n}$. The probability of sampling $r=0$ is $1-p$:

| $n$ | $p = \sqrt{\log n / n}$ | $P(r=0) = 1-p$ | Expected $\#$vertices with $r \geq 1$ |
|---|---|---|---|
| 10 | 0.480 | 52.0% | 4.8 |
| 50 | 0.303 | 69.7% | 15.2 |
| 100 | 0.214 | 78.6% | 21.4 |
| 200 | 0.155 | 84.5% | 31.0 |

Only $\approx n \cdot p$ vertices (those with $r \geq 1$) can ever generate tree edges. However, each such vertex dominates all its lower-label neighbours, so in a dense graph a single high-radius vertex can create many tree edges. For $n=200$: ~31 vertices have $r \geq 1$ and collectively produce 187 tree edges (4.5% of the spanner). The remaining 95.5% are cross edges. The $n \cdot p$ figure therefore bounds the number of *propagating vertices*, not directly the number of tree edges — but it correctly predicts that tree edges are a minority.

Cross edges are generated whenever vertex $y$ encounters a new base value $B(P(x)) \notin M(y)$. In dense graphs with many distinct base values, this happens far more frequently than tree propagation.

---

### Randomness & Variance Analysis

> **$K_{50}$, $t=2$, 10 independent seeds** — coefficient of variation (CV) = **7.47%**

![Variance K_50](results/analysis_variance_K50.png)

| Seed | $\lvert H \rvert$ |
|---|---|
| 1000 | 479 |
| 1001 | 384 |
| 1002 | 414 |
| 1003 | 389 |
| 1004 | 411 |
| 1005 | 387 |
| 1006 | 392 |
| 1007 | 399 |
| 1008 | 433 |
| 1009 | 446 |
| **Range** | **384–479** |
| **Mean** | 413.4 |
| **Std dev** | 30.9 |

A CV of $7.47\%$ confirms that the algorithm is robust. The with-high-probability bounds of \[1\] translate into genuine stability — different random seeds and edge orderings produce consistently similar spanner sizes.

---

## 6. Full Results Table

All 60 scenarios. Columns: $n$ = vertices, $t$ = stretch parameter, $|E|$ = original edges, $|H|$ = spanner size, Bound = paper formula value, $r_b$ = $|H|$/Bound, $r_c$ = $|H|$/$|E|$, MaxD = max observed distance for adjacent pairs.

| Scenario | $n$ | $t$ | $\lvert E \rvert$ | $\lvert H \rvert$ | Bound | $r_b$ | $r_c$ | MaxD | Is Valid? |
|---|---|---|---|---|---|---|---|---|---|
| Dense ER $n=30$ | 30 | 2 | 215 | 132 | 606 | 0.218 | 0.614 | 3 | ✓         |
| Dense ER $n=50$ | 50 | 2 | 628 | 379 | 1,398 | 0.271 | 0.604 | 3 | ✓         |
| Dense ER $n=75$ | 75 | 2 | 1,363 | 635 | 2,699 | 0.235 | 0.466 | 3 | ✓         |
| Dense ER $n=100$ | 100 | 2 | 2,462 | 1,132 | 4,291 | 0.264 | 0.460 | 3 | ✓         |
| ER $n=100$, $m=150$ | 100 | 2 | 150 | 150 | 4,291 | 0.035 | 1.000 | 1 | ✓         |
| ER $n=100$, $m=300$ | 100 | 2 | 300 | 294 | 4,291 | 0.069 | 0.980 | 3 | ✓         |
| ER $n=100$, $m=500$ | 100 | 2 | 500 | 476 | 4,291 | 0.111 | 0.952 | 3 | ✓         |
| ER $n=100$, $m=800$ | 100 | 2 | 800 | 688 | 4,291 | 0.160 | 0.860 | 3 | ✓         |
| ER $n=100$, $m=1200$ | 100 | 2 | 1,200 | 858 | 4,291 | 0.200 | 0.715 | 3 | ✓         |
| ER $n=100$, $m=2000$ | 100 | 2 | 2,000 | 978 | 4,291 | 0.228 | 0.489 | 3 | ✓         |
| ER $n=100$, $m=500$, $t=3$ | 100 | 3 | 500 | 455 | 3,854 | 0.118 | 0.910 | 3 | ✓         |
| ER $n=100$, $m=2000$, $t=3$ | 100 | 3 | 2,000 | 787 | 3,854 | 0.204 | 0.394 | 3 | ✓         |
| Grid $5{\times}5$ | 25 | 2 | 40 | 39 | 448 | 0.087 | 0.975 | 3 | ✓         |
| Grid $5{\times}5$, $t=3$ | 25 | 3 | 40 | 38 | 478 | 0.079 | 0.950 | 3 | ✓         |
| Grid $8{\times}8$ | 64 | 2 | 112 | 107 | 2,088 | 0.051 | 0.955 | 3 | ✓         |
| Grid $8{\times}8$, $t=3$ | 64 | 3 | 112 | 110 | 1,986 | 0.055 | 0.982 | 3 | ✓         |
| Grid $10{\times}10$ | 100 | 2 | 180 | 174 | 4,291 | 0.041 | 0.967 | 3 | ✓         |
| Grid $10{\times}10$, $t=3$ | 100 | 3 | 180 | 176 | 3,854 | 0.046 | 0.978 | 3 | ✓         |
| Grid $15{\times}15$ | 225 | 2 | 420 | 412 | 15,708 | 0.026 | 0.981 | 3 | ✓         |
| Grid $15{\times}15$, $t=3$ | 225 | 3 | 420 | 410 | 12,661 | 0.032 | 0.976 | 3 | ✓         |
| $K_{10}$ | 10 | 2 | 45 | 30 | 95 | 0.316 | 0.667 | 2 | ✓         |
| $K_{20}$ | 20 | 2 | 190 | 68 | 309 | 0.220 | 0.358 | 3 | ✓         |
| $K_{30}$ | 30 | 2 | 435 | 180 | 606 | 0.297 | 0.414 | 3 | ✓         |
| $K_{50}$ | 50 | 2 | 1,225 | 585 | 1,398 | 0.418 | 0.478 | 2 | ✓         |
| $K_{75}$ | 75 | 2 | 2,775 | 821 | 2,699 | 0.304 | 0.296 | 3 | ✓         |
| $K_{100}$ | 100 | 2 | 4,950 | 1,126 | 4,291 | 0.262 | 0.227 | 3 | ✓         |
| $K_{150}$ | 150 | 2 | 11,175 | 2,378 | 8,224 | 0.289 | 0.213 | 3 | ✓         |
| $K_{200}$ | 200 | 2 | 19,900 | 4,201 | 13,020 | 0.323 | 0.211 | 3 | ✓         |
| Path $P_{20}$ | 20 | 2 | 19 | 19 | 309 | 0.061 | 1.000 | 1 | ✓         |
| Path $P_{50}$ | 50 | 2 | 49 | 49 | 1,398 | 0.035 | 1.000 | 1 | ✓         |
| Path $P_{100}$ | 100 | 2 | 99 | 99 | 4,291 | 0.023 | 1.000 | 1 | ✓         |
| Cycle $C_{20}$ | 20 | 2 | 20 | 20 | 309 | 0.065 | 1.000 | 1 | ✓         |
| Cycle $C_{50}$ | 50 | 2 | 50 | 50 | 1,398 | 0.036 | 1.000 | 1 | ✓         |
| Cycle $C_{100}$ | 100 | 2 | 100 | 100 | 4,291 | 0.023 | 1.000 | 1 | ✓         |
| Star $S_{20}$ | 20 | 2 | 19 | 19 | 309 | 0.061 | 1.000 | 1 | ✓         |
| Star $S_{50}$ | 50 | 2 | 49 | 49 | 1,398 | 0.035 | 1.000 | 1 | ✓         |
| Star $S_{100}$ | 100 | 2 | 99 | 99 | 4,291 | 0.023 | 1.000 | 1 | ✓         |
| RandTree $T_{20}$ | 20 | 2 | 19 | 19 | 309 | 0.061 | 1.000 | 1 | ✓         |
| RandTree $T_{50}$ | 50 | 2 | 49 | 49 | 1,398 | 0.035 | 1.000 | 1 | ✓         |
| RandTree $T_{100}$ | 100 | 2 | 99 | 99 | 4,291 | 0.023 | 1.000 | 1 | ✓         |
| $K_{50}$, $t=2$ | 50 | 2 | 1,225 | 450 | 1,398 | 0.322 | 0.367 | 3 | ✓         |
| $K_{50}$, $t=3$ | 50 | 3 | 1,225 | 243 | 1,371 | 0.177 | 0.198 | 3 | ✓         |
| $K_{50}$, $t=4$ | 50 | 4 | 1,225 | 219 | 1,479 | 0.148 | 0.179 | 3 | ✓         |
| $K_{100}$, $t=2$ | 100 | 2 | 4,950 | 1,129 | 4,291 | 0.263 | 0.228 | 3 | ✓         |
| $K_{100}$, $t=3$ | 100 | 3 | 4,950 | 951 | 3,854 | 0.247 | 0.192 | 3 | ✓ |
| $K_{100}$, $t=4$ | 100 | 4 | 4,950 | 695 | 3,976 | 0.175 | 0.140 | 3 | ✓ |
| $K_{50}$ rep 0–9 | 50 | 2 | 1,225 | 384–479 | 1,398 | — | — | ≤3 | ✓ |
| ER $n=30$, $m=60$, $t=3$ | 30 | 3 | 60 | 57 | 606 | 0.090 | 0.950 | 4 | ✓ |
| ER $n=50$, $m=75$, $t=3$ | 50 | 3 | 75 | 71 | 1,371 | 0.052 | 0.947 | 5 | ✓ |
| ER $n=30$, $m=45$, $t=4$ | 30 | 4 | 45 | 43 | 703 | 0.061 | 0.956 | 5 | ✓ |
| ER $n=50$, $m=100$, $t=4$ | 50 | 4 | 100 | 97 | 1,479 | 0.066 | 0.970 | 6 | ✓ |

---

## 7. Analysis & Conclusions

### Hypothesis Summary

| ID | Hypothesis | Verdict | Key Evidence |
|---|---|---|---|
| H1 | $(2t-1)$-stretch correctness | **✓ CONFIRMED** | 60/60 pass, $\max \text{dist} = 3$ for $t=2$ |
| H2 | Size $\sim O(n^{3/2})$ | **✓ CONFIRMED** | Log-log slope $= 1.663 \approx 1.5$ |
| H3 | Higher $t$ $\Rightarrow$ smaller spanner | **✓ CONFIRMED** | $K_{100}$: $1129 \to 951 \to 695$ for $t=2,3,4$ |
| H4 | Denser $\Rightarrow$ more compression | **✓ CONFIRMED** | ER $n=100$: ratio $1.0 \to 0.49$ as $m$ grows |
| H5 | Sparse graphs lossless | **✓ CONFIRMED** | All stars/trees/paths: ratio $= 1.000$ |
| H6 | Actual $<$ theoretical bound | **✓ CONFIRMED** | 100% below bound; $2.4$–$43\times$ smaller |
| H7 | Cross edges dominate | **✓ CONFIRMED** | $85.8\%$ avg cross fraction in dense graphs |

### Conclusion 1: The Stretch Guarantee is Exact and Universal

Theorem 3.2 of \[1\] holds without exception across all 60 scenarios and 8 graph families. The label-propagation mechanism of Algorithm 1 faithfully enforces the $(2t-1)$-stretch bound in practice, even under random edge orderings. Sparse graphs (paths, stars, trees) achieve distance 1 — far better than the bound. Dense graphs reach the bound exactly for $t=2$, and the tight-bound ER scenarios confirm the guarantee is sharp for higher $t$ values too (max dist 5 for $t=3$ bound=5, max dist 6 for $t=4$ bound=7).

### Conclusion 2: The Size Bound is Tight in Exponent, Conservative in Constant

The empirical growth rate (slope 1.663) closely tracks the $O(n^{3/2})$ prediction of Corollary 3.6 \[1\]. The slight deviation above 1.5 is attributable to the $\sqrt{\log n}$ correction term in the bound. Actual sizes are consistently **2–43× below** the bound, confirming that Corollary 3.6 is a worst-case ceiling rather than a tight predictor.

### Conclusion 3: The $t$ Parameter Offers a Practical Size/Stretch Trade-off

The exponent $1+1/t$ in Corollary 3.6 \[1\] translates directly to observable size reductions. Increasing $t$ from 2 to 4 reduces the spanner size of $K_{100}$ by $\approx 38\%$, while the stretch guarantee loosens from 3 to 7. The marginal benefit decreases as $t$ grows (matching the diminishing gap between $1+1/t$ values), providing a quantitative tool for selecting $t$ in practice.

### Conclusion 4: The Algorithm Self-Saturates on Dense Graphs

For dense graphs the spanner size grows slowly and saturates near the $O(n^{3/2})$ ceiling regardless of $|E|$. The spanner size in H4 grows from 476 to 978 as $m$ goes from 500 to 2000 — roughly doubling while the original graph grows 4×, and the growth rate slows toward the ceiling. This means the algorithm automatically discards redundant edges without requiring knowledge of the graph's density. This is a key practical advantage of the streaming model.

### Conclusion 5: Cross Edges Are the Primary Spanner Mechanism

The most counter-intuitive finding: cross edges constitute **70–96%** of spanner edges in complete graphs. This follows directly from the radius distribution: $P(r=0) = 1-p \approx 1 - \sqrt{\log n / n}$, meaning only $O(p) = O(\sqrt{\log n / n})$ fraction of vertices contribute tree edges. Cross-edge detection is therefore the dominant mechanism in practice — the algorithm keeps most edges because each vertex encounters base values it has not seen before, not because of label propagation.

### Conclusion 6: The Algorithm is Stable Under Randomness

A CV of $7.47\%$ across 10 independent seeds confirms genuine stability. The with-high-probability bounds of \[1\] reflect this: the truncated geometric radius distribution concentrates well around its mean, making the algorithm reliable for practical deployment.

---

## 8. Bibliography

**\[1\]** Elkin, M. (2011). *Streaming and Fully Dynamic Centralized Algorithms for Constructing and Maintaining Sparse Spanners.* ACM Transactions on Algorithms (TALG), **7**(2), Article 20.  
DOI: [10.1145/1921659.1921666](https://doi.org/10.1145/1921659.1921666)  
*Primary source. All algorithm details (Algorithm 1, Section 3.1–3.4), the stretch guarantee (Theorem 3.2), and the size bound (Corollary 3.6) are taken directly from this paper.*

**\[2\]** Peleg, D., and Schäffer, A.A. (1989). *Graph Spanners.* Journal of Graph Theory, **13**(1), pp. 99–116.  
*Introduced the concept of graph spanners and proved the $\Omega(n^{1+1/t})$ lower bound for $(2t-1)$-spanners, establishing that Elkin's algorithm is near-optimal up to log factors.*

**\[3\]** Erdős, P. (1963). *Extremal problems in graph theory.* In A Seminar in Graph Theory, pp. 54–59. Holt, Rinehart and Winston.  
*Original source of the girth conjecture: an $n$-vertex graph with more than $\frac{1}{2}n^{1+1/t}$ edges must contain a cycle of length $\leq 2t$. This implies any $(2t-1)$-spanner requires $\Omega(n^{1+1/t})$ edges in the worst case.*

**\[4\]** Althöfer, I., Das, G., Dobkin, D., Joseph, D., and Soares, J. (1993). *On Sparse Spanners of Weighted Graphs.* Discrete & Computational Geometry, **9**(1), pp. 81–100.  
*Greedy offline algorithm achieving $O(n^{1+1/t})$-size spanners. Provides the offline baseline against which Elkin's streaming algorithm is compared in \[1\].*

---

*Report generated from `analyze_results.py` — all plots in `results/analysis_*.png`*