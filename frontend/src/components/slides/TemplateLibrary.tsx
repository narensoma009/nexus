import type { PPTTemplate } from "@/types";

export function TemplateLibrary({
  templates,
  selectedId,
  onSelect,
}: {
  templates: PPTTemplate[];
  selectedId?: string;
  onSelect: (t: PPTTemplate) => void;
}) {
  return (
    <div className="space-y-2">
      {templates.map((t) => (
        <button
          key={t.id}
          onClick={() => onSelect(t)}
          className={`block w-full text-left rounded-lg border p-3 transition ${
            selectedId === t.id ? "border-brand-500 bg-cyan-50" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <div className="font-medium text-slate-900 text-sm">{t.name}</div>
          <div className="text-xs text-slate-500 mt-1">
            {t.slide_count} slides{t.tags ? ` · ${t.tags}` : ""}
          </div>
        </button>
      ))}
      {!templates.length && <div className="text-sm text-slate-500">No templates yet.</div>}
    </div>
  );
}
