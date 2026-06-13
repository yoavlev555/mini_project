/** Elkin 2011 Algorithm 1 — mirrors streaming_spanner.py */

export type EdgeDecision = 'tree' | 'cross' | 'drop';

export interface SpannerEdge {
  u: number;
  v: number;
  decision: EdgeDecision;
}

export interface VertexState {
  id: number;
  r: number;
  P: number;
  B: number;
  L: number;
  M: number[];
}

function createRng(seed: number): () => number {
  let s = seed >>> 0;
  return () => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 0x100000000;
  };
}

export class StreamingSpanner {
  readonly n: number;
  readonly t: number;
  readonly p: number;

  private readonly radius: number[];
  private readonly label: number[];
  private readonly M: Set<number>[];
  private readonly rng: () => number;
  private readonly spannerEdges: SpannerEdge[] = [];
  private readonly streamed = new Set<string>();

  constructor(n: number, t: number, seed = 0) {
    if (n < 1 || t < 1) throw new Error('n and t must be positive');
    this.n = n;
    this.t = t;
    this.p = (Math.log(Math.max(n, 2)) / Math.max(n, 2)) ** (1 / t);
    this.rng = createRng(seed);
    this.radius = Array.from({ length: n + 1 }, () => 0);
    this.label = Array.from({ length: n + 1 }, () => 0);
    this.M = Array.from({ length: n + 1 }, () => new Set<number>());

    for (let v = 1; v <= n; v++) {
      this.radius[v] = this.sampleRadius();
      this.label[v] = v;
    }
  }

  private edgeKey(u: number, v: number): string {
    return u < v ? `${u},${v}` : `${v},${u}`;
  }

  private level(P: number): number {
    return Math.floor((P - 1) / this.n);
  }

  private base(P: number): number {
    return ((P - 1) % this.n) + 1;
  }

  private isSelected(P: number): boolean {
    return this.level(P) < this.radius[this.base(P)];
  }

  private dominates(u: number, v: number): boolean {
    const pu = this.label[u];
    const pv = this.label[v];
    return pu > pv || (pu === pv && u > v);
  }

  private sampleRadius(): number {
    for (let k = 0; k < this.t - 1; k++) {
      if (this.rng() >= this.p) return k;
    }
    return this.t - 1;
  }

  /** Returns null if this undirected edge was already streamed. */
  readEdge(u: number, v: number): EdgeDecision | null {
    if (u === v) return null;
    const key = this.edgeKey(u, v);
    if (this.streamed.has(key)) return null;
    this.streamed.add(key);

    const [x, y] = this.dominates(u, v) ? [u, v] : [v, u];
    const px = this.label[x];

    if (this.isSelected(px)) {
      this.label[y] = px + this.n;
      this.spannerEdges.push({ u, v, decision: 'tree' });
      return 'tree';
    }

    const bx = this.base(px);
    if (!this.M[y].has(bx)) {
      this.M[y].add(bx);
      this.spannerEdges.push({ u, v, decision: 'cross' });
      return 'cross';
    }

    return 'drop';
  }

  getVertices(): VertexState[] {
    const out: VertexState[] = [];
    for (let id = 1; id <= this.n; id++) {
      const P = this.label[id];
      out.push({
        id,
        r: this.radius[id],
        P,
        B: this.base(P),
        L: this.level(P),
        M: [...this.M[id]].sort((a, b) => a - b),
      });
    }
    return out;
  }

  getSpannerEdges(): SpannerEdge[] {
    return [...this.spannerEdges];
  }

  hasStreamedEdge(u: number, v: number): boolean {
    return this.streamed.has(this.edgeKey(u, v));
  }
}
