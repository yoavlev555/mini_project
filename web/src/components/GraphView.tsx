import type { SpannerEdge, VertexState } from '../algorithm/streamingSpanner';

const CX = 400;
const CY = 200;
const R = 150;

interface Props {
  vertices: VertexState[];
  edges: SpannerEdge[];
  selectedId: number | null;
  onNodeClick: (id: number) => void;
}

function position(id: number, n: number) {
  const angle = ((id - 1) / n) * 2 * Math.PI - Math.PI / 2;
  return {
    x: CX + R * Math.cos(angle),
    y: CY + R * Math.sin(angle),
    angle,
  };
}

export function GraphView({ vertices, edges, selectedId, onNodeClick }: Props) {
  const n = vertices.length;
  const pos = new Map(vertices.map((v) => [v.id, position(v.id, n)]));

  return (
    <svg className="graph" viewBox="0 0 800 400">
      <g>
        {edges.map((e) => {
          const a = pos.get(e.u)!;
          const b = pos.get(e.v)!;
          return (
            <line
              key={`${e.u}-${e.v}-${e.decision}`}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              className={e.decision === 'tree' ? 'edge-tree' : 'edge-cross'}
            />
          );
        })}
      </g>
      <g>
        {vertices.map((v) => {
          const p = pos.get(v.id)!;
          const outward = 28;
          const lx = p.x + outward * Math.cos(p.angle);
          const ly = p.y + outward * Math.sin(p.angle);
          return (
            <g key={v.id}>
              <circle
                cx={p.x}
                cy={p.y}
                r={20}
                className={`node ${selectedId === v.id ? 'selected' : ''}`}
                onClick={() => onNodeClick(v.id)}
              />
              <text x={p.x} y={p.y} className="node-label">
                {v.id}
              </text>
              <text
                x={lx}
                y={ly}
                className="node-meta"
                textAnchor={Math.cos(p.angle) > 0 ? 'start' : 'end'}
              >
                {`r:${v.r} P:${v.P}`}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
}
