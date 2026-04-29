import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useTree } from "@/hooks/useHierarchyNode";
import { HierarchyTree } from "@/components/hierarchy/HierarchyTree";
import { UploadZone } from "@/components/shared/UploadZone";
import { bulkImportResources } from "@/api/resources";

export function AdminPage() {
  const { data: tree } = useTree();
  const [report, setReport] = useState<any | null>(null);

  const importer = useMutation({
    mutationFn: (file: File) => bulkImportResources(file),
    onSuccess: setReport,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Admin</h1>

      <section className="space-y-2">
        <h2 className="font-semibold">Bulk import resources (CSV)</h2>
        <UploadZone accept=".csv" onFile={(f) => importer.mutate(f)} label="Drop a CSV with columns: name, email, role, seniority, team_id" />
        {report && (
          <pre className="text-xs bg-white border border-slate-200 rounded p-3 overflow-auto">
            {JSON.stringify(report, null, 2)}
          </pre>
        )}
      </section>

      <section>
        <h2 className="font-semibold mb-2">Hierarchy</h2>
        <HierarchyTree nodes={tree ?? []} />
      </section>
    </div>
  );
}
