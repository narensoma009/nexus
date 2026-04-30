import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  fetchTemplates, generateSlides, fetchJob, downloadJob, uploadTemplate,
} from "@/api/slides";
import { TemplateGrid } from "@/components/slides/TemplateGrid";
import { PlaceholderMap } from "@/components/slides/PlaceholderMap";
import { UploadZone } from "@/components/shared/UploadZone";
import { usePrograms } from "@/hooks/usePrograms";
import { asArray } from "@/utils/array";
import type { PPTTemplate } from "@/types";
import { ArrowLeft, Download, Loader2 } from "lucide-react";

export function SlideGeneratorPage() {
  const qc = useQueryClient();
  const { data: templates, isLoading } = useQuery({
    queryKey: ["templates"], queryFn: fetchTemplates,
  });
  const { data: programs } = usePrograms();

  const [selected, setSelected] = useState<PPTTemplate | null>(null);
  const [programId, setProgramId] = useState<string>("");
  const [period, setPeriod] = useState<string>("");
  const [jobId, setJobId] = useState<string | null>(null);

  const upload = useMutation({
    mutationFn: ({ file, name }: { file: File; name: string }) => uploadTemplate(file, name, ""),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["templates"] }),
  });

  const generate = useMutation({
    mutationFn: () =>
      generateSlides({
        template_id: selected!.id,
        program_id: programId || undefined,
        period,
      }),
    onSuccess: (data) => setJobId(data.job_id),
  });

  const job = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => fetchJob(jobId!),
    enabled: !!jobId,
    refetchInterval: (q) => {
      const status = (q.state.data as any)?.status;
      return status === "completed" || status === "failed" ? false : 1500;
    },
  });

  const handleDownload = async () => {
    if (!jobId) return;
    const blob = await downloadJob(jobId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${selected?.name ?? "presentation"}_${jobId.slice(0, 8)}.pptx`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const placeholders = selected ? safeParse(selected.placeholder_map) : [];
  const templateList = asArray<PPTTemplate>(templates);

  // STEP 1 — Pick a template
  if (!selected) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Generate a presentation</h1>
          <p className="text-slate-600 text-sm mt-1">
            Step 1 of 2 — choose a template, or upload a new one.
          </p>
        </div>

        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold">
              Available templates
              <span className="text-slate-400 font-normal ml-2 text-sm">
                ({templateList.length})
              </span>
            </h2>
          </div>
          {isLoading ? (
            <div className="text-slate-500 text-sm">Loading templates…</div>
          ) : (
            <TemplateGrid
              templates={templateList}
              selectedId={undefined}
              onSelect={(t) => {
                setSelected(t);
                setJobId(null);
              }}
            />
          )}
        </section>

        <section>
          <h2 className="font-semibold mb-2">Upload new template</h2>
          <UploadZone
            accept=".pptx"
            onFile={(f) => upload.mutate({ file: f, name: f.name })}
            label={
              upload.isPending
                ? "Uploading…"
                : "Drop a .pptx with {{TOKEN}} placeholders, or click to browse"
            }
          />
        </section>
      </div>
    );
  }

  // STEP 2 — Configure + generate
  return (
    <div className="space-y-6 max-w-4xl">
      <button
        onClick={() => {
          setSelected(null);
          setJobId(null);
        }}
        className="flex items-center gap-1 text-sm text-slate-600 hover:text-slate-900"
      >
        <ArrowLeft size={14} /> Back to templates
      </button>

      <div>
        <h1 className="text-2xl font-semibold">{selected.name}</h1>
        <div className="text-sm text-slate-500 mt-1">
          {selected.slide_count} slides · {placeholders.length} placeholders
        </div>
      </div>

      <section className="rounded-lg border border-slate-200 bg-white p-4 space-y-4">
        <h2 className="font-semibold">Configure</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm text-slate-600 block mb-1">Program</label>
            <select
              className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm focus:outline-none focus:border-brand-500"
              value={programId}
              onChange={(e) => setProgramId(e.target.value)}
            >
              <option value="">— none / all programs —</option>
              {asArray(programs).map((p: any) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
            <div className="text-xs text-slate-500 mt-1">
              Used to populate program-specific data tokens.
            </div>
          </div>

          <div>
            <label className="text-sm text-slate-600 block mb-1">Period</label>
            <input
              className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm focus:outline-none focus:border-brand-500"
              placeholder="Q2 2026"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
            />
            <div className="text-xs text-slate-500 mt-1">
              Filled into <code>{"{{PERIOD}}"}</code> / <code>{"{{QUARTER}}"}</code> tokens.
            </div>
          </div>
        </div>
      </section>

      <section>
        <h2 className="font-semibold mb-2">Placeholders detected</h2>
        <PlaceholderMap placeholders={placeholders} />
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <button
            onClick={() => generate.mutate()}
            disabled={generate.isPending || job.data?.status === "running" || job.data?.status === "queued"}
            className="bg-brand-500 hover:bg-brand-600 disabled:bg-slate-300 text-white rounded px-5 py-2 text-sm font-medium flex items-center gap-2"
          >
            {generate.isPending && <Loader2 size={14} className="animate-spin" />}
            {jobId ? "Regenerate" : "Generate presentation"}
          </button>

          {job.data && (
            <div className="text-sm text-slate-700 flex items-center gap-2">
              <StatusDot status={job.data.status} />
              <span>Status: <strong>{job.data.status}</strong></span>
              {job.data.status === "completed" && (
                <button
                  onClick={handleDownload}
                  className="ml-2 inline-flex items-center gap-1 bg-emerald-500 hover:bg-emerald-600 text-white rounded px-3 py-1.5 text-sm"
                >
                  <Download size={14} /> Download .pptx
                </button>
              )}
              {job.data.error && (
                <span className="text-rose-600 text-xs">— {job.data.error}</span>
              )}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

function StatusDot({ status }: { status: string }) {
  const colors: Record<string, string> = {
    queued: "bg-slate-400",
    running: "bg-amber-500 animate-pulse",
    completed: "bg-emerald-500",
    failed: "bg-rose-500",
  };
  return <span className={`inline-block w-2 h-2 rounded-full ${colors[status] ?? "bg-slate-300"}`} />;
}

function safeParse(raw: string): { token: string; type: string }[] {
  try {
    return JSON.parse(raw || "[]");
  } catch {
    return [];
  }
}
