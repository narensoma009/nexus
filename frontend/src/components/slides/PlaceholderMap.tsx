interface Placeholder {
  token: string;
  type: string;
  description?: string;
}

export function PlaceholderMap({ placeholders }: { placeholders: Placeholder[] }) {
  if (!placeholders.length)
    return <div className="text-sm text-slate-500">No placeholders detected.</div>;
  return (
    <div className="rounded border border-slate-200 bg-white">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-3 py-2 text-left font-medium text-slate-600">Token</th>
            <th className="px-3 py-2 text-left font-medium text-slate-600">Type</th>
            <th className="px-3 py-2 text-left font-medium text-slate-600">Description</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {placeholders.map((p) => (
            <tr key={p.token}>
              <td className="px-3 py-2 font-mono text-xs">{p.token}</td>
              <td className="px-3 py-2">
                <span className="text-xs bg-slate-100 px-2 py-0.5 rounded">{p.type}</span>
              </td>
              <td className="px-3 py-2 text-slate-600">{p.description ?? ""}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
