import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import type { TrendPoint } from "@/types";

export function TrendChart({ points }: { points: TrendPoint[] }) {
  // Pivot: each tool becomes its own line series
  const tools = Array.from(new Set(points.map((p) => p.tool_name)));
  const dates = Array.from(new Set(points.map((p) => p.date.slice(0, 10))));
  const data = dates.map((d) => {
    const row: Record<string, any> = { date: d };
    for (const t of tools) {
      const m = points.find((p) => p.date.startsWith(d) && p.tool_name === t);
      row[t] = m?.sessions ?? 0;
    }
    return row;
  });

  if (!data.length) return <div className="text-sm text-slate-500">No trend data.</div>;
  const palette = ["#0e7490", "#0891b2", "#7c3aed", "#f59e0b", "#10b981"];

  return (
    <div className="h-64 rounded border border-slate-200 bg-white p-3">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" fontSize={11} />
          <YAxis fontSize={11} />
          <Tooltip />
          <Legend />
          {tools.map((t, i) => (
            <Line key={t} type="monotone" dataKey={t} stroke={palette[i % palette.length]} strokeWidth={2} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
