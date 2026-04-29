import type { HeatmapCell } from "@/types";

const STAGE_COLOR: Record<string, string> = {
  piloting: "bg-slate-200 text-slate-800",
  onboarded: "bg-sky-200 text-sky-900",
  active: "bg-teal-300 text-teal-900",
  embedded: "bg-emerald-500 text-white",
};

export function AdoptionHeatMap({ cells }: { cells: HeatmapCell[] }) {
  const teams = Array.from(new Set(cells.map((c) => c.team_name)));
  const tools = Array.from(new Set(cells.map((c) => c.tool_name)));
  const lookup = new Map(cells.map((c) => [`${c.team_name}|${c.tool_name}`, c]));

  if (!cells.length) return <div className="text-sm text-slate-500">No adoption data yet.</div>;

  return (
    <div className="overflow-auto rounded border border-slate-200 bg-white">
      <table className="min-w-full text-xs">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-2 py-2 text-left font-medium text-slate-600">Team</th>
            {tools.map((t) => (
              <th key={t} className="px-2 py-2 text-left font-medium text-slate-600">
                {t}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {teams.map((team) => (
            <tr key={team} className="border-t border-slate-100">
              <td className="px-2 py-2 font-medium">{team}</td>
              {tools.map((tool) => {
                const cell = lookup.get(`${team}|${tool}`);
                return (
                  <td key={tool} className="px-2 py-2">
                    {cell ? (
                      <span className={`inline-block px-2 py-0.5 rounded ${STAGE_COLOR[cell.stage] ?? "bg-slate-100"}`}>
                        {cell.stage} ({cell.user_count})
                      </span>
                    ) : (
                      <span className="text-slate-300">—</span>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
