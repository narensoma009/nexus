import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchTemplates, generateSlides, fetchJob, downloadJob, uploadTemplate } from "@/api/slides";
import { TemplateLibrary } from "@/components/slides/TemplateLibrary";
import { PlaceholderMap } from "@/components/slides/PlaceholderMap";
import { UploadZone } from "@/components/shared/UploadZone";
import { usePrograms } from "@/hooks/usePrograms";
import type { PPTTemplate } from "@/types";

export function SlideGeneratorPage() {
  const qc = useQueryClient();
  const { data: templates } = useQuery({ queryKey: ["templates"], queryFn: fetchTemplates });
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
      generateSlides({ template_id: selected!.id, program_id: programId || undefined, period }),
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
    a.download = `generated_${jobId}.pptx`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const placeholders = selected ? JSON.parse(selected.placeholder_map || "[]") : [];

  return (
    <div className="flex gap-6">
      <aside className="w-56 shrink-0 space-y-3">
        <h2 className="font-semibold">Templates</h2>
        <TemplateLibrary
          templates={templates ?? []}
          selectedId={selected?.id}
          onSelect={setSelected}
        />
        <UploadZone
          accept=".pptx"
          onFile={(f) => upload.mutate({ file: f, name: f.name })}
          label="Upload .pptx"
        />
      </aside>

      <div className="flex-1 space-y-4">
        <h1 className="text-2xl font-semibold">Slide Generator</h1>
        {selected ? (
          <>
            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <div className="font-semibold">{selected.name}</div>
              <div className="text-xs text-slate-500">{selected.slide_count} slides</div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-sm text-slate-600">Program</label>
                <select
                  className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
                  value={programId}
                  onChange={(e) => setProgramId(e.target.value)}
                >
                  <option value="">— none —</option>
                  {(programs ?? []).map((p: any) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm text-slate-600">Period</label>
                <input
                  className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
                  placeholder="Q2 2026"
                  value={period}
                  onChange={(e) => setPeriod(e.target.value)}
                />
              </div>
            </div>

            <section>
              <h2 className="font-semibold mb-2">Placeholders</h2>
              <PlaceholderMap placeholders={placeholders} />
            </section>

            <div className="flex items-center gap-3">
              <button
                onClick={() => generate.mutate()}
                disabled={generate.isPending}
                className="bg-brand-500 hover:bg-brand-600 text-white rounded px-4 py-2 text-sm"
              >
                Generate slides
              </button>
              {job.data && (
                <span className="text-sm text-slate-600">
                  Status: {job.data.status}
                  {job.data.status === "completed" && (
                    <button onClick={handleDownload} className="ml-3 text-brand-600 underline">
                      Download
                    </button>
                  )}
                </span>
              )}
            </div>
          </>
        ) : (
          <div className="text-slate-500">Select or upload a template to begin.</div>
        )}
      </div>
    </div>
  );
}
