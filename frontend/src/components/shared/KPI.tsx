interface Props {
  label: string;
  value: number | string;
  sub?: string;
  icon: React.ReactNode;
  accent: string; // tailwind gradient classes, e.g. "from-brand-500 to-cyan-500"
}

export function KPI({ label, value, sub, icon, accent }: Props) {
  return (
    <div className="relative rounded-xl border border-slate-200 bg-white p-4 overflow-hidden">
      <div
        className={`absolute inset-y-0 left-0 w-1 bg-gradient-to-b ${accent}`}
        aria-hidden
      />
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">
            {label}
          </div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{value}</div>
          {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
        </div>
        <div className={`bg-gradient-to-br ${accent} text-white rounded-lg p-2`}>{icon}</div>
      </div>
    </div>
  );
}
