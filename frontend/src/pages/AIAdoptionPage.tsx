import { useQuery } from "@tanstack/react-query";
import { fetchTools, fetchSummary, fetchHeatmap, fetchTrends } from "@/api/aiAdoption";
import { ToolCard } from "@/components/ai-adoption/ToolCard";
import { AdoptionHeatMap } from "@/components/ai-adoption/AdoptionHeatMap";
import { TrendChart } from "@/components/ai-adoption/TrendChart";

export function AIAdoptionPage() {
  const { data: tools } = useQuery({ queryKey: ["tools"], queryFn: fetchTools });
  const { data: summary } = useQuery({ queryKey: ["adoption-summary"], queryFn: fetchSummary });
  const { data: heatmap } = useQuery({ queryKey: ["adoption-heatmap"], queryFn: fetchHeatmap });
  const { data: trends } = useQuery({ queryKey: ["adoption-trends"], queryFn: fetchTrends });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">AI Adoption</h1>

      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Stat label="Active users %" value={`${summary.active_pct}%`} />
          <Stat label="Active users" value={summary.active_users} />
          <Stat label="Tools tracked" value={summary.tools_tracked} />
          <Stat label="Avg stage score" value={summary.avg_stage_score} />
        </div>
      )}

      <section>
        <h2 className="font-semibold mb-2">Heat map</h2>
        <AdoptionHeatMap cells={heatmap ?? []} />
      </section>

      <section>
        <h2 className="font-semibold mb-2">Tools</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {(tools ?? []).map((t: any) => <ToolCard key={t.id} tool={t} />)}
        </div>
      </section>

      <section>
        <h2 className="font-semibold mb-2">Usage trends</h2>
        <TrendChart points={trends ?? []} />
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="text-xs text-slate-500">{label}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}
