export function NodeCard({
  title,
  subtitle,
  metrics,
}: {
  title: string;
  subtitle?: string;
  metrics?: { label: string; value: string | number }[];
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="font-semibold text-slate-900">{title}</div>
      {subtitle && <div className="text-xs text-slate-500 mt-0.5">{subtitle}</div>}
      {metrics && (
        <div className="grid grid-cols-2 gap-2 mt-3">
          {metrics.map((m) => (
            <div key={m.label}>
              <div className="text-xs text-slate-500">{m.label}</div>
              <div className="text-lg font-semibold text-slate-900">{m.value}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
