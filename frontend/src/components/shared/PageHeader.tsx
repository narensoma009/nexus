export function PageHeader({
  kicker,
  title,
  subtitle,
  actions,
}: {
  kicker?: string;
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}) {
  return (
    <header className="flex items-end justify-between gap-4 flex-wrap">
      <div>
        {kicker && (
          <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">
            {kicker}
          </div>
        )}
        <h1 className="text-3xl font-bold text-slate-900 mt-1">{title}</h1>
        {subtitle && <p className="text-slate-600 text-sm mt-1">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </header>
  );
}
