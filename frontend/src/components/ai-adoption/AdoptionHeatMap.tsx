import type { HeatmapCell } from "@/types";

const STAGE_STYLES: Record<string, { bg: string; text: string }> = {
  piloting: { bg: "bg-slate-200", text: "text-slate-700" },
  onboarded: { bg: "bg-sky-200", text: "text-sky-900" },
  active: { bg: "bg-teal-300", text: "text-teal-900" },
  embedded: { bg: "bg-emerald-500", text: "text-white" },
};

export function AdoptionHeatMap({ cells }: { cells: HeatmapCell[] }) {
  const teams = Array.from(new Set(cells.map((c) => c.team_name)));
  const tools = Array.from(new Set(cells.map((c) => c.tool_name)));
  const lookup = new Map(cells.map((c) => [`${c.team_name}|${c.tool_name}`, c]));

  if (!cells.length)
    return <div className="text-sm text-slate-400 italic py-6 text-center">No adoption data yet.</div>;

  return (
    <div className="overflow-auto">
      <table className="min-w-full text-xs border-separate border-spacing-1">
        <thead>
          <tr>
            <th className="text-left font-semibold text-slate-600 pl-2 pr-4 sticky left-0 bg-white z-10">
              Team
            </th>
            {tools.map((t) => (
              <th
                key={t}
                className="text-left font-semibold text-slate-600 px-2 py-1 whitespace-nowrap"
              >
                {t}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {teams.map((team) => (
            <tr key={team} className="hover:bg-slate-50/50">
              <td className="pl-2 pr-4 py-1 font-medium text-slate-800 whitespace-nowrap sticky left-0 bg-white">
                {team}
              </td>
              {tools.map((tool) => {
                const cell = lookup.get(`${team}|${tool}`);
                if (!cell) {
                  return (
                    <td key={tool} className="px-2 py-1 text-slate-300">
                      —
                    </td>
                  );
                }
                const style = STAGE_STYLES[cell.stage] ?? STAGE_STYLES.piloting;
                return (
                  <td key={tool} className="px-1 py-1">
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 ${style.bg} ${style.text} text-[11px] font-medium whitespace-nowrap`}
                      title={`${cell.stage}: ${cell.user_count} users`}
                    >
                      {cell.stage}
                      <span className="bg-white/40 rounded px-1 tabular-nums">
                        {cell.user_count}
                      </span>
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex gap-4 text-xs text-slate-600 mt-3 pt-3 border-t border-slate-100">
        {Object.entries(STAGE_STYLES).map(([stage, s]) => (
          <div key={stage} className="flex items-center gap-1.5">
            <span className={`w-3 h-3 rounded ${s.bg}`} />
            {stage}
          </div>
        ))}
      </div>
    </div>
  );
}
