import { useCallback, useMemo, useState } from 'react';
import { StreamingSpanner } from './algorithm/streamingSpanner';
import { GraphView } from './components/GraphView';
import { LogPanel, type LogEntry } from './components/LogPanel';
import { StateTable } from './components/StateTable';
import './App.css';

const MIN_N = 2;
const MAX_N = 30;

interface SimParams {
  n: number;
  t: number;
  seed: number;
}

export default function App() {
  const [screen, setScreen] = useState<'setup' | 'sim'>('setup');
  const [form, setForm] = useState<SimParams>({ n: 7, t: 2, seed: 0 });
  const [algo, setAlgo] = useState<StreamingSpanner | null>(null);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [tick, setTick] = useState(0);
  const [logs, setLogs] = useState<LogEntry[]>([]);

  const appendLog = useCallback((kind: LogEntry['kind'], text: string) => {
    setLogs((prev) => [...prev, { id: prev.length + 1, kind, text }]);
  }, []);

  const start = () => {
    const n = Math.min(MAX_N, Math.max(MIN_N, form.n));
    const t = Math.max(1, form.t);
    const instance = new StreamingSpanner(n, t, form.seed);
    setForm((f) => ({ ...f, n, t }));
    setAlgo(instance);
    setSelectedId(null);
    setTick(0);
    setLogs([
      {
        id: 1,
        kind: 'info',
        text: `Started: n=${n}, t=${t}, stretch<=${2 * t - 1}, seed=${form.seed}. Click two vertices to stream an edge.`,
      },
    ]);
    setScreen('sim');
  };

  const reset = () => {
    if (!algo) return;
    const instance = new StreamingSpanner(algo.n, algo.t, form.seed);
    setAlgo(instance);
    setSelectedId(null);
    setTick(0);
    setLogs([{ id: 1, kind: 'info', text: 'Simulation reset (same n, t, seed).' }]);
  };

  const handleNodeClick = (id: number) => {
    if (!algo) return;

    if (selectedId === null) {
      setSelectedId(id);
      return;
    }
    if (selectedId === id) {
      setSelectedId(null);
      return;
    }

    const u = selectedId;
    const v = id;
    setSelectedId(null);

    if (algo.hasStreamedEdge(u, v)) {
      appendLog('muted', `Edge [${u}-${v}] already in stream — ignored.`);
      setTick((x) => x + 1);
      return;
    }

    const before = algo.getVertices();
    const pu = before.find((p) => p.id === u)!;
    const pv = before.find((p) => p.id === v)!;
    const dom = pu.P > pv.P || (pu.P === pv.P && u > v) ? u : v;
    const other = dom === u ? v : u;
    const d = before.find((p) => p.id === dom)!;
    const level = Math.floor((d.P - 1) / algo.n);
    const base = ((d.P - 1) % algo.n) + 1;
    const rootR = before.find((p) => p.id === base)!.r;

    const decision = algo.readEdge(u, v);
    if (!decision) return;

    if (decision === 'tree') {
      const newP = algo.getVertices().find((p) => p.id === other)!.P;
      appendLog(
        'tree',
        `Tree [${u}-${v}]: P(${dom}) selected (L=${level} < r=${rootR}). Vertex ${other} → P=${newP}.`,
      );
    } else if (decision === 'cross') {
      appendLog('cross', `Cross [${u}-${v}]: base ${base} added to M(${other}).`);
    } else {
      appendLog('drop', `Drop [${u}-${v}]: base ${base} already in M(${other}).`);
    }

    setTick((x) => x + 1);
  };

  const vertices = useMemo(() => algo?.getVertices() ?? [], [algo, tick]);
  const edges = useMemo(() => algo?.getSpannerEdges() ?? [], [algo, tick]);

  if (screen === 'setup') {
    return (
      <div className="app">
        <div className="panel">
          <h1>Elkin Streaming Spanner — Simulator</h1>
          <p className="hint">
            Set parameters, then add edges one at a time and watch Algorithm 1 decide tree / cross / drop.
          </p>
          <div className="setup-form">
            <div className="field">
              <label htmlFor="n">Vertices n ({MIN_N}-{MAX_N})</label>
              <input
                id="n"
                type="number"
                min={MIN_N}
                max={MAX_N}
                value={form.n}
                onChange={(e) => setForm({ ...form, n: Number(e.target.value) })}
              />
            </div>
            <div className="field">
              <label htmlFor="t">Stretch param t</label>
              <input
                id="t"
                type="number"
                min={1}
                max={10}
                value={form.t}
                onChange={(e) => setForm({ ...form, t: Number(e.target.value) })}
              />
            </div>
            <div className="field">
              <label htmlFor="seed">Random seed</label>
              <input
                id="seed"
                type="number"
                value={form.seed}
                onChange={(e) => setForm({ ...form, seed: Number(e.target.value) })}
              />
            </div>
            <button type="button" onClick={start}>
              Start simulation
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <div className="panel">
        <div className="header">
          <h1>
            Elkin Spanner (n={algo!.n}, t={algo!.t}, stretch &lt;= {2 * algo!.t - 1})
          </h1>
          <div>
            <button type="button" className="secondary" onClick={reset}>
              Reset
            </button>{' '}
            <button type="button" className="secondary" onClick={() => setScreen('setup')}>
              Change params
            </button>
          </div>
        </div>
        <p className="hint">Click one vertex, then another, to stream an edge between them.</p>
        <GraphView
          vertices={vertices}
          edges={edges}
          selectedId={selectedId}
          onNodeClick={handleNodeClick}
        />
        <div className="bottom">
          <StateTable vertices={vertices} />
          <LogPanel entries={logs} />
        </div>
      </div>
    </div>
  );
}
