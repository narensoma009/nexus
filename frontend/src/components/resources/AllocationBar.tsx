export function AllocationBar({ pct }: { pct: number }) {
  const clamped = Math.max(0, Math.min(100, pct));
  const color = clamped > 100 ? "bg-rose-500" : clamped > 80 ? "bg-amber-500" : "bg-emerald-500";
  return (
    <div className="w-full bg-slate-100 rounded h-2 overflow-hidden">
      <div className={`${color} h-full`} style={{ width: `${clamped}%` }} />
    </div>
  );
}
