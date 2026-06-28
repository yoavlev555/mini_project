/* Frontend for the Elkin spanner simulator.
   The algorithm is the real streaming_spanner.py, executed in the browser via
   Pyodide. The only Python defined here is a thin glue layer that exposes
   JSON-returning start/edge/reset helpers — no algorithm logic in JS. */

const CX = 400, CY = 200, R = 150;

const state = {
  vertices: [],
  edges: [],
  selectedId: null,
};

let py = null;

// --- DOM refs ---
const setupScreen = document.getElementById('setup-screen');
const simScreen = document.getElementById('sim-screen');
const graph = document.getElementById('graph');
const stateBody = document.getElementById('state-body');
const logEl = document.getElementById('log');
const simTitle = document.getElementById('sim-title');
const startBtn = document.getElementById('start-btn');

// --- Thin Python glue: wraps the real StreamingSpanner, returns JSON ---
const GLUE = `
import json

class _Sim:
    algo = None
    streamed = set()
    n = 0
    t = 0
    seed = 0

def _vertices():
    a = _Sim.algo
    out = []
    for v in range(1, a.n + 1):
        p = a.label[v]
        out.append({"id": v, "r": a.radius[v], "P": p,
                    "B": ((p - 1) % a.n) + 1, "L": (p - 1) // a.n,
                    "M": sorted(a.M[v])})
    return out

def _edges():
    a = _Sim.algo
    e = []
    for v in range(1, a.n + 1):
        for x, y in a.T[v]:
            e.append({"u": x, "v": y, "decision": "tree"})
        for x, y in a.X[v]:
            e.append({"u": x, "v": y, "decision": "cross"})
    return e

def start(n, t, seed):
    n = max(2, min(30, int(n)))
    t = max(1, int(t))
    seed = int(seed)
    _Sim.algo = StreamingSpanner(n, t, seed=seed)
    _Sim.streamed = set()
    _Sim.n, _Sim.t, _Sim.seed = n, t, seed
    return json.dumps({"n": n, "t": t, "seed": seed, "stretch": 2 * t - 1,
                       "vertices": _vertices(), "edges": _edges()})

def edge(u, v):
    a = _Sim.algo
    u, v = int(u), int(v)
    if u == v:
        return json.dumps({"error": "self-loop"})
    key = (min(u, v), max(u, v))
    if key in _Sim.streamed:
        return json.dumps({"decision": "duplicate",
                           "message": f"Edge [{u}-{v}] already in stream - ignored.",
                           "vertices": _vertices(), "edges": _edges()})
    pu, pv = a.label[u], a.label[v]
    dom = u if (pu > pv or (pu == pv and u > v)) else v
    other = v if dom == u else u
    pd = a.label[dom]
    level = (pd - 1) // a.n
    base = ((pd - 1) % a.n) + 1
    root_r = a.radius[base]
    d = a.read_edge(u, v)
    _Sim.streamed.add(key)
    if d == "tree":
        np_ = a.label[other]
        msg = f"Tree [{u}-{v}]: P({dom}) selected (L={level} < r={root_r}). Vertex {other} -> P={np_}."
    elif d == "cross":
        msg = f"Cross [{u}-{v}]: base {base} added to M({other})."
    else:
        msg = f"Drop [{u}-{v}]: base {base} already in M({other})."
    return json.dumps({"decision": d, "message": msg,
                       "vertices": _vertices(), "edges": _edges()})

def reset():
    _Sim.algo = StreamingSpanner(_Sim.n, _Sim.t, seed=_Sim.seed)
    _Sim.streamed = set()
    return json.dumps({"vertices": _vertices(), "edges": _edges()})
`;

// Call a Python glue function and parse its JSON result.
function pyCall(name, ...args) {
  const fn = py.globals.get(name);
  const out = fn(...args);
  fn.destroy();
  return JSON.parse(out);
}

// --- Boot Pyodide and load the real algorithm ---
async function boot() {
  py = await loadPyodide();
  const src = await (await fetch('streaming_spanner.py')).text();
  py.runPython(src + '\n' + GLUE);
  startBtn.disabled = false;
  startBtn.textContent = 'Start simulation';
}

// --- Geometry ---
function position(id, n) {
  const angle = ((id - 1) / n) * 2 * Math.PI - Math.PI / 2;
  return { x: CX + R * Math.cos(angle), y: CY + R * Math.sin(angle), angle };
}

// --- Logging ---
function appendLog(kind, text) {
  const div = document.createElement('div');
  div.className = `log-entry log-${kind}`;
  div.textContent = text;
  logEl.appendChild(div);
  logEl.scrollTop = logEl.scrollHeight;
}

// --- Rendering ---
function render() {
  const n = state.vertices.length;
  const pos = new Map(state.vertices.map((v) => [v.id, position(v.id, n)]));

  const edgeSvg = state.edges.map((e) => {
    const a = pos.get(e.u), b = pos.get(e.v);
    const cls = e.decision === 'tree' ? 'edge-tree' : 'edge-cross';
    return `<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" class="${cls}" />`;
  }).join('');

  const nodeSvg = state.vertices.map((v) => {
    const p = pos.get(v.id);
    const out = 28;
    const lx = p.x + out * Math.cos(p.angle);
    const ly = p.y + out * Math.sin(p.angle);
    const anchor = Math.cos(p.angle) > 0 ? 'start' : 'end';
    const sel = state.selectedId === v.id ? 'selected' : '';
    return `<g>
      <circle cx="${p.x}" cy="${p.y}" r="20" class="node ${sel}" data-id="${v.id}" />
      <text x="${p.x}" y="${p.y}" class="node-label">${v.id}</text>
      <text x="${lx}" y="${ly}" class="node-meta" text-anchor="${anchor}">r:${v.r} P:${v.P}</text>
    </g>`;
  }).join('');

  graph.innerHTML = `<g>${edgeSvg}</g><g>${nodeSvg}</g>`;

  stateBody.innerHTML = state.vertices.map((v) => `
    <tr>
      <td><strong>${v.id}</strong></td>
      <td>${v.r}</td>
      <td><strong>${v.P}</strong></td>
      <td>${v.B}</td>
      <td>${v.L}</td>
      <td>[${v.M.join(', ')}]</td>
    </tr>`).join('');
}

// --- Interaction ---
function onNodeClick(id) {
  if (state.selectedId === null) {
    state.selectedId = id;
    render();
    return;
  }
  if (state.selectedId === id) {
    state.selectedId = null;
    render();
    return;
  }

  const u = state.selectedId;
  const v = id;
  state.selectedId = null;

  const data = pyCall('edge', u, v);
  if (data.error) { render(); return; }

  state.vertices = data.vertices;
  state.edges = data.edges;
  const kind = data.decision === 'duplicate' ? 'muted' : data.decision;
  appendLog(kind, data.message);
  render();
}

graph.addEventListener('click', (e) => {
  const id = e.target.getAttribute && e.target.getAttribute('data-id');
  if (id) onNodeClick(Number(id));
});

// --- Start / reset / navigation ---
function start() {
  const n = Number(document.getElementById('n').value);
  const t = Number(document.getElementById('t').value);
  const seed = Number(document.getElementById('seed').value);

  const data = pyCall('start', n, t, seed);
  state.vertices = data.vertices;
  state.edges = data.edges;
  state.selectedId = null;

  simTitle.textContent = `Elkin Spanner (n=${data.n}, t=${data.t}, stretch <= ${data.stretch})`;
  logEl.innerHTML = '';
  appendLog('info', `Started: n=${data.n}, t=${data.t}, stretch<=${data.stretch}, seed=${data.seed}. Click two vertices to stream an edge.`);

  setupScreen.hidden = true;
  simScreen.hidden = false;
  render();
}

function reset() {
  const data = pyCall('reset');
  state.vertices = data.vertices;
  state.edges = data.edges;
  state.selectedId = null;
  logEl.innerHTML = '';
  appendLog('info', 'Simulation reset (same n, t, seed).');
  render();
}

startBtn.addEventListener('click', start);
document.getElementById('reset-btn').addEventListener('click', reset);
document.getElementById('change-btn').addEventListener('click', () => {
  simScreen.hidden = true;
  setupScreen.hidden = false;
});

boot();
