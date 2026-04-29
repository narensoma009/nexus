import { Link } from "@tanstack/react-router";
import { StatusBadge } from "../shared/StatusBadge";
import type { Program } from "@/types";

export function ProgramCard({ program }: { program: Program }) {
  return (
    <Link
      to="/programs/$programId"
      params={{ programId: program.id }}
      className="block rounded-lg border border-slate-200 bg-white p-4 hover:shadow-md transition"
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold text-slate-900">{program.name}</h3>
        <StatusBadge status={program.status} />
      </div>
      {program.description && (
        <p className="text-sm text-slate-600 line-clamp-2 mb-3">{program.description}</p>
      )}
      <div className="text-xs text-slate-500">
        {program.start_date && `Starts ${new Date(program.start_date).toLocaleDateString()}`}
      </div>
    </Link>
  );
}
