import type { PPTTemplate } from "@/types";
import { Trash2 } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteTemplate } from "@/api/slides";

export function TemplateLibrary({
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
    if (!confirm(`Delete template "${t.name}"? This removes the file and any embeddings.`)) return;
    remove.mutate(t.id);
  };

  return (
    <div className="space-y-2">
      {templates.map((t) => (
        <div
          key={t.id}
          onClick={() => onSelect(t)}
          className={`group flex items-start justify-between gap-2 rounded-lg border p-3 transition cursor-pointer ${
            selectedId === t.id
              ? "border-brand-500 bg-cyan-50"
              : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <div className="min-w-0">
            <div className="font-medium text-slate-900 text-sm truncate">{t.name}</div>
            <div className="text-xs text-slate-500 mt-1">
              {t.slide_count} slides{t.tags ? ` · ${t.tags}` : ""}
            </div>
          </div>
          <button
            onClick={(e) => handleDelete(e, t)}
            disabled={remove.isPending}
            className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 transition shrink-0"
            aria-label={`Delete ${t.name}`}
          >
            <Trash2 size={16} />
          </button>
        </div>
      ))}
      {!templates.length && <div className="text-sm text-slate-500">No templates yet.</div>}
    </div>
  );
}
