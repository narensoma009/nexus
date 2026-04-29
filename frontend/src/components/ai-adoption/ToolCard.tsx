import type { AITool } from "@/types";

export function ToolCard({ tool }: { tool: AITool }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="font-semibold text-slate-900">{tool.name}</div>
          <div className="text-xs text-slate-500">{tool.vendor}</div>
        </div>
        <span className="text-xs bg-slate-100 px-2 py-0.5 rounded">{tool.category}</span>
      </div>
      {tool.target_user_count !== undefined && (
        <div className="mt-3 text-xs text-slate-500">Target users: {tool.target_user_count}</div>
      )}
    </div>
  );
}
