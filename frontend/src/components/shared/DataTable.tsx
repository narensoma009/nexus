interface Column<T> {
  key: keyof T | string;
  label: string;
  render?: (row: T) => React.ReactNode;
}

export function DataTable<T extends Record<string, any>>({
  rows,
  columns,
  empty = "No data",
}: {
  rows: T[];
  columns: Column<T>[];
  empty?: string;
}) {
  if (!rows.length) {
    return <div className="text-sm text-slate-500 py-6 text-center">{empty}</div>;
  }
  return (
    <div className="overflow-auto rounded border border-slate-200 bg-white">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50 text-left">
          <tr>
            {columns.map((c) => (
              <th key={String(c.key)} className="px-3 py-2 font-medium text-slate-600">
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {rows.map((r, i) => (
            <tr key={i} className="hover:bg-slate-50">
              {columns.map((c) => (
                <td key={String(c.key)} className="px-3 py-2">
                  {c.render ? c.render(r) : String(r[c.key as keyof T] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
