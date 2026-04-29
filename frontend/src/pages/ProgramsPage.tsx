import { usePrograms } from "@/hooks/usePrograms";
import { ProgramCard } from "@/components/programs/ProgramCard";
import type { Program } from "@/types";

export function ProgramsPage() {
  const { data, isLoading } = usePrograms();

  return (
    <div>
      <h1 className="text-2xl font-semibold mb-6">Programs</h1>
      {isLoading && <div className="text-slate-500">Loading…</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(data ?? []).map((p: Program) => (
          <ProgramCard key={p.id} program={p} />
        ))}
      </div>
      {data && data.length === 0 && <div className="text-slate-500">No programs yet.</div>}
    </div>
  );
}
