import clsx from "clsx";

const STATUS_STYLES: Record<string, string> = {
  on_track: "bg-emerald-100 text-emerald-800",
  at_risk: "bg-amber-100 text-amber-800",
  planning: "bg-sky-100 text-sky-800",
  completed: "bg-slate-200 text-slate-700",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={clsx(
        "inline-block px-2 py-0.5 rounded text-xs font-medium",
        STATUS_STYLES[status] ?? "bg-slate-100 text-slate-700"
      )}
    >
      {status.replace("_", " ")}
    </span>
  );
}
