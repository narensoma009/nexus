import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useTree } from "@/hooks/useHierarchyNode";
import { HierarchyTree } from "@/components/hierarchy/HierarchyTree";
import { UploadZone } from "@/components/shared/UploadZone";
import { bulkImportResources } from "@/api/resources";
import { bulkImportProjects, reloadCategorizationRules } from "@/api/programs";
import { asArray } from "@/utils/array";

export function AdminPage() {
  const qc = useQueryClient();
  const { data: tree } = useTree();
  const [resourceReport, setResourceReport] = useState<any | null>(null);
  const [projectReport, setProjectReport] = useState<any | null>(null);

  const resourceImporter = useMutation({
    mutationFn: (file: File) => bulkImportResources(file),
    onSuccess: setResourceReport,
  });

  const projectImporter = useMutation({
    mutationFn: (file: File) => bulkImportProjects(file),
    onSuccess: (r) => {
      setProjectReport(r);
      qc.invalidateQueries({ queryKey: ["programs-with-projects"] });
      qc.invalidateQueries({ queryKey: ["programs"] });
    },
  });

  const reloadRules = useMutation({
    mutationFn: reloadCategorizationRules,
  });

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold">Admin</h1>

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="font-semibold">Import projects (CSV or XLSX)</h2>
          <button
            onClick={() => reloadRules.mutate()}
            className="text-xs text-brand-600 hover:underline"
            disabled={reloadRules.isPending}
          >
            Reload categorization rules
          </button>
        </div>
        <p className="text-sm text-slate-600">
          Required column: <code className="bg-slate-100 px-1 rounded">project_name</code>.
          Optional: <code className="bg-slate-100 px-1 rounded">description</code>,{" "}
          <code className="bg-slate-100 px-1 rounded">program</code>,{" "}
          <code className="bg-slate-100 px-1 rounded">portfolio</code>,{" "}
          <code className="bg-slate-100 px-1 rounded">team</code>,{" "}
          <code className="bg-slate-100 px-1 rounded">status</code>,{" "}
          <code className="bg-slate-100 px-1 rounded">start_date</code>,{" "}
          <code className="bg-slate-100 px-1 rounded">end_date</code>.
          If <code className="bg-slate-100 px-1 rounded">program</code> is missing, projects are
          auto-categorized using keyword rules.
        </p>
        <UploadZone
          accept=".csv,.xlsx"
          onFile={(f) => projectImporter.mutate(f)}
          label="Drop a project spreadsheet (.csv or .xlsx) or click to upload"
        />
        {projectImporter.isPending && (
          <div className="text-sm text-slate-500">Importing…</div>
        )}
        {projectReport && <ImportReport report={projectReport} kind="projects" />}
      </section>

      <section className="space-y-2">
        <h2 className="font-semibold">Import resources (CSV)</h2>
        <UploadZone
          accept=".csv"
          onFile={(f) => resourceImporter.mutate(f)}
          label="Drop a CSV with columns: name, email, role, seniority, team_id"
        />
        {resourceReport && (
          <pre className="text-xs bg-white border border-slate-200 rounded p-3 overflow-auto max-h-64">
            {JSON.stringify(resourceReport, null, 2)}
          </pre>
        )}
      </section>

      <section>
        <h2 className="font-semibold mb-2">Hierarchy</h2>
        <HierarchyTree nodes={asArray(tree)} />
      </section>
    </div>
  );
}

function ImportReport({ report, kind }: { report: any; kind: string }) {
  const byProgram = report.by_program ?? {};
  const errors = report.errors ?? [];
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 space-y-3">
      <div className="flex items-center gap-3 text-sm">
        <span className="bg-emerald-100 text-emerald-800 rounded px-2 py-0.5">
          {report.imported} {kind} imported
        </span>
        {errors.length > 0 && (
          <span className="bg-rose-100 text-rose-800 rounded px-2 py-0.5">
            {errors.length} errors
          </span>
        )}
      </div>

      {Object.keys(byProgram).length > 0 && (
        <div>
          <div className="text-sm font-medium text-slate-700 mb-1">Categorization breakdown</div>
          <ul className="text-sm text-slate-600 space-y-1">
            {Object.entries(byProgram).map(([prog, count]) => (
              <li key={prog} className="flex justify-between">
                <span>{prog}</span>
                <span className="font-mono text-xs">{count as number}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {errors.length > 0 && (
        <details>
          <summary className="text-sm cursor-pointer text-rose-700">Show errors</summary>
          <pre className="text-xs mt-2 max-h-48 overflow-auto">
            {JSON.stringify(errors, null, 2)}
          </pre>
        </details>
      )}
    </div>
  );
}
