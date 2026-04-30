import { useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { fetchResource, fetchResourceAssignments } from "@/api/resources";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { DataTable } from "@/components/shared/DataTable";
import { AllocationBar } from "@/components/resources/AllocationBar";
import { asArray } from "@/utils/array";

export function ResourcePage() {
  const { resourceId } = useParams({ from: "/resources/$resourceId" });
  const { data: resource } = useQuery({
    queryKey: ["resource", resourceId],
    queryFn: () => fetchResource(resourceId),
  });
  const { data: assignments } = useQuery({
    queryKey: ["resource", resourceId, "assignments"],
    queryFn: () => fetchResourceAssignments(resourceId),
  });

  if (!resource) return <div className="text-slate-500">Loading…</div>;

  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: "Resources" }, { label: resource.name }]} />
      <div>
        <h1 className="text-2xl font-semibold">{resource.name}</h1>
        <div className="text-slate-600">{resource.role} · {resource.seniority}</div>
        <div className="text-xs text-slate-500">{resource.email}</div>
      </div>

      <section>
        <h2 className="font-semibold mb-2">Assignments</h2>
        <DataTable
          rows={asArray(assignments)}
          columns={[
            { key: "role", label: "Role" },
            {
              key: "allocation_pct", label: "Allocation",
              render: (r: any) => (
                <div className="flex items-center gap-2">
                  <span className="w-10 text-xs">{r.allocation_pct}%</span>
                  <div className="flex-1"><AllocationBar pct={r.allocation_pct} /></div>
                </div>
              ),
            },
            { key: "workstream_id", label: "Workstream" },
          ]}
        />
      </section>
    </div>
  );
}
