import type { PPTTemplate } from "@/types";
import { FileText, Trash2, CheckCircle2 } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteTemplate } from "@/api/slides";

interface Placeholder {
  token: string;
  type: string;
}

export function TemplateGrid({
  templates,
  selectedId,
  onSelect,
}: {
  templates: PPTTemplate[];
  selectedId?: string;
  onSelect: (t: PPTTemplate) => void;
}) {
  const qc = useQueryClient();

  const remove = useMutation({
    mutationFn: (id: string) => deleteTemplate(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["templates"] }),
  });

  const handleDelete = (e: React.MouseEvent, t: PPTTemplate) => {
    e.stopPropagation();
    if (!confirm(`Delete "${t.name}"? This removes the file and any embeddings.`)) return;
    remove.mutate(t.id);
  };

  if (!templates.length) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center">
        <FileText size={32} className="mx-auto text-slate-400 mb-2" />
        <div className="font-medium text-slate-700">No templates uploaded</div>
        <div className="text-sm text-slate-500 mt-1">
          Upload a .pptx with <code className="bg-slate-100 px-1 rounded">{"{{TOKEN}}"}</code> placeholders to get started.
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      {templates.map((t) => {
        const placeholders = parsePlaceholders(t.placeholder_map);
        const dataCount = placeholders.filter((p) => p.type === "data" || p.type === "auto").length;
        const aiCount = placeholders.filter((p) => p.type === "ai").length;
        const tableCount = placeholders.filter((p) => p.type === "table").length;
        const isSelected = selectedId === t.id;

        return (
          <div
            key={t.id}
            onClick={() => onSelect(t)}
            className={`group relative rounded-lg border bg-white p-4 cursor-pointer transition ${
              isSelected
                ? "border-brand-500 ring-2 ring-brand-500 ring-opacity-30 shadow-sm"
                : "border-slate-200 hover:border-slate-400 hover:shadow-sm"
            }`}
          >
            {isSelected && (
              <CheckCircle2
                size={20}
                className="absolute top-3 right-3 text-brand-500 fill-cyan-50"
              />
            )}

            <div className="flex items-start gap-3 mb-3">
              <div className="bg-slate-100 rounded p-2 shrink-0">
                <FileText size={20} className="text-slate-600" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="font-semibold text-slate-900 text-sm truncate">{t.name}</div>
                <div className="text-xs text-slate-500 mt-0.5">
                  {t.slide_count} slides
                  {t.tags ? ` · ${t.tags}` : ""}
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-1.5 text-xs">
              {dataCount > 0 && <Chip label={`${dataCount} data`} color="slate" />}
              {tableCount > 0 && <Chip label={`${tableCount} tables`} color="sky" />}
              {aiCount > 0 && <Chip label={`${aiCount} AI`} color="violet" />}
              {placeholders.length === 0 && <Chip label="no placeholders" color="amber" />}
            </div>

            <div className="text-xs text-slate-400 mt-3">
              Uploaded {new Date(t.uploaded_at).toLocaleDateString()}
              {t.last_used_at && ` · last used ${new Date(t.last_used_at).toLocaleDateString()}`}
            </div>

            <button
              onClick={(e) => handleDelete(e, t)}
              disabled={remove.isPending}
              className="absolute bottom-3 right-3 opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 transition"
              aria-label={`Delete ${t.name}`}
            >
              <Trash2 size={14} />
            </button>
          </div>
        );
      })}
    </div>
  );
}

function Chip({ label, color }: { label: string; color: "slate" | "sky" | "violet" | "amber" }) {
  const styles = {
    slate: "bg-slate-100 text-slate-700",
    sky: "bg-sky-100 text-sky-800",
    violet: "bg-violet-100 text-violet-800",
    amber: "bg-amber-100 text-amber-800",
  };
  return <span className={`px-2 py-0.5 rounded ${styles[color]}`}>{label}</span>;
}

function parsePlaceholders(raw: string): Placeholder[] {
  try {
    return JSON.parse(raw || "[]");
  } catch {
    return [];
  }
}
