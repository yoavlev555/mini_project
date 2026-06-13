export interface LogEntry {
  id: number;
  kind: 'info' | 'tree' | 'cross' | 'drop' | 'muted';
  text: string;
}

export function LogPanel({ entries }: { entries: LogEntry[] }) {
  return (
    <div className="log-wrap">
      {entries.map((e) => (
        <div key={e.id} className={`log-entry log-${e.kind}`}>
          {e.text}
        </div>
      ))}
    </div>
  );
}
