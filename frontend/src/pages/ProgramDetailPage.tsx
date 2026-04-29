import { useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useProgram, usePortfolioSpread } from "@/hooks/usePrograms";
import { fetchProgramWorkstreams, fetchProgramResources } from "@/api/programs";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { PortfolioSpreadMatrix } from "@/components/programs/PortfolioSpreadMatrix";
import { RosterTable } from "@/components/resources/RosterTable";
import { DataTable } from "@/components/shared/DataTable";

export function ProgramDetailPage() {
  const { programId } = useParams({ from: "/programs/$programId" });
  const { data: program } = useProgram(programId);
  const { data: spread } = usePortfolioSpread(programId);
  const { data: workstreams } = useQuery({
    queryKey: ["program", programId, "workstreams"],
    queryFn: () => fetchProgramWorkstreams(programId),
  });
  const { data: resources } = useQuery({
    queryKey: ["program", programId, "resources"],
    queryFn: () => fetchProgramResources(programId),
  });

  if (!program) return <div className="text-slate-500">Loading…</div>;

  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: "Programs", to: "/" }, { label: program.name }]} />
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{program.name}</h1>
          {program.description && <p className="text-slate-600 mt-1">{program.description}</p>}
        </div>
        <StatusBadge status={program.status} />
      </div>

      <section>
        <h2 className="font-semibold mb-2">Portfolio spread</h2>
        <PortfolioSpreadMatrix entries={spread ?? []} />
      </section>

      <section>
        <h2 className="font-semibold mb-2">Workstreams</h2>
        <DataTable
          rows={workstreams ?? []}
          columns={[
            { key: "name", label: "Name" },
            { key: "status", label: "Status", render: (r: any) => <StatusBadge status={r.status} /> },
          ]}
        />
      </section>

      <section>
        <h2 className="font-semibold mb-2">Resources</h2>
        <RosterTable rows={resources ?? []} />
      </section>
    </div>
  );
}
