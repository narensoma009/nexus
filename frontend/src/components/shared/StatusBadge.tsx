import clsx from "clsx";

const STATUS_STYLES: Record<string, string> = {
  on_track: "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200",
  at_risk: "bg-amber-50 text-amber-700 ring-1 ring-amber-200",
  planning: "bg-sky-50 text-sky-700 ring-1 ring-sky-200",
  completed: "bg-slate-100 text-slate-600 ring-1 ring-slate-200",
};

const STATUS_DOT: Record<string, string> = {
  on_track: "bg-emerald-500",
  at_risk: "bg-amber-500",
  planning: "bg-sky-500",
  completed: "bg-slate-400",
};

export function StatusBadge({ status }: { status: string }) {
  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-medium",
        STATUS_STYLES[status] ?? "bg-slate-100 text-slate-700 ring-1 ring-slate-200"
      )}
    >
      <span className={clsx("h-1.5 w-1.5 rounded-full", STATUS_DOT[status] ?? "bg-slate-400")} />
      {status.replace("_", " ")}
    </span>
  );
}
