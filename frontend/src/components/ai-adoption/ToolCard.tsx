import type { AITool } from "@/types";
import { Sparkles, Cpu, FileText, Database, Bot } from "lucide-react";

const CATEGORY_ICON: Record<string, React.ReactNode> = {
  code_assist: <Cpu size={16} />,
  agentic: <Bot size={16} />,
  doc_gen: <FileText size={16} />,
  data: <Database size={16} />,
  other: <Sparkles size={16} />,
};

const CATEGORY_GRADIENT: Record<string, string> = {
  code_assist: "from-brand-500 to-cyan-500",
  agentic: "from-violet-500 to-fuchsia-500",
  doc_gen: "from-amber-500 to-orange-500",
  data: "from-emerald-500 to-teal-500",
  other: "from-slate-500 to-slate-600",
};

export function ToolCard({ tool }: { tool: AITool }) {
  const gradient = CATEGORY_GRADIENT[tool.category] ?? CATEGORY_GRADIENT.other;
  const icon = CATEGORY_ICON[tool.category] ?? CATEGORY_ICON.other;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 hover:shadow-md hover:border-slate-300 transition">
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="font-semibold text-slate-900">{tool.name}</div>
          <div className="text-xs text-slate-500">{tool.vendor}</div>
        </div>
        <div className={`bg-gradient-to-br ${gradient} text-white rounded-lg p-2`}>
          {icon}
        </div>
      </div>

      <div className="flex items-center gap-2 flex-wrap">
        <span className="text-[11px] uppercase tracking-wider bg-slate-100 text-slate-700 rounded px-2 py-0.5 font-semibold">
          {tool.category.replace("_", " ")}
        </span>
        {tool.target_user_count !== undefined && tool.target_user_count !== null && (
          <span className="text-xs text-slate-500">
            Target: <span className="font-medium text-slate-700">{tool.target_user_count}</span>
          </span>
        )}
      </div>

      {tool.rollout_date && (
        <div className="text-xs text-slate-400 mt-3">
          Rolled out {new Date(tool.rollout_date).toLocaleDateString()}
        </div>
      )}
    </div>
  );
}
