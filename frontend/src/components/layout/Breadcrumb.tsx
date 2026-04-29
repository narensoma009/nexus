export function Breadcrumb({ items }: { items: { label: string; to?: string }[] }) {
  return (
    <nav className="text-sm text-slate-500 mb-3">
      {items.map((it, i) => (
        <span key={i}>
          {i > 0 && <span className="mx-1.5">/</span>}
          <span className={i === items.length - 1 ? "text-slate-800 font-medium" : ""}>
            {it.label}
          </span>
        </span>
      ))}
    </nav>
  );
}
