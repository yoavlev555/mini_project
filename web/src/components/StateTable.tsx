import type { VertexState } from '../algorithm/streamingSpanner';

export function StateTable({ vertices }: { vertices: VertexState[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>r</th>
            <th>P</th>
            <th>B</th>
            <th>L</th>
            <th>M</th>
          </tr>
        </thead>
        <tbody>
          {vertices.map((v) => (
            <tr key={v.id}>
              <td>
                <strong>{v.id}</strong>
              </td>
              <td>{v.r}</td>
              <td>
                <strong>{v.P}</strong>
              </td>
              <td>{v.B}</td>
              <td>{v.L}</td>
              <td>[{v.M.join(', ')}]</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
