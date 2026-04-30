import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchTools, fetchSummary, fetchHeatmap, fetchTrends } from "@/api/aiAdoption";
import { fetchPortfoliosSummary } from "@/api/hierarchy";
import { asArray } from "@/utils/array";
import { ToolCard } from "@/components/ai-adoption/ToolCard";
import { AdoptionHeatMap } from "@/components/ai-adoption/AdoptionHeatMap";
import { TrendChart } from "@/components/ai-adoption/TrendChart";
import { KPI } from "@/components/shared/KPI";
import { PageHeader } from "@/components/shared/PageHeader";
import { Sparkles, Users, Wrench, Gauge } from "lucide-react";

export function AIAdoptionPage() {
  const [portfolioId, setPortfolioId] = useState<string>("");
  const scope = portfolioId || undefined;

  const { data: portfolios } = useQuery({
    queryKey: ["portfolios-summary"],
    queryFn: fetchPortfoliosSummary,
  });
  const { data: tools } = useQuery({
    queryKey: ["tools", portfolioId],
    queryFn: () => fetchTools(scope),
  });
  const { data: summary } = useQuery({
    queryKey: ["adoption-summary", portfolioId],
    queryFn: () => fetchSummary(scope),
  });
  const { data: heatmap } = useQuery({
    queryKey: ["adoption-heatmap", portfolioId],
    queryFn: () => fetchHeatmap(scope),
  });
  const { data: trends } = useQuery({
    queryKey: ["adoption-trends", portfolioId],
    queryFn: () => fetchTrends(scope),
  });

  const portfolioList = asArray<{ id: string; name: string }>(portfolios);
  const selected = portfolioList.find((p) => p.id === portfolioId);

  return (
    <div className="space-y-6">
      <PageHeader
        kicker="Capability dashboard"
        title="AI Adoption"
        subtitle={
          selected
            ? `Scoped to ${selected.name}`
            : "Account-wide rollout, license, and usage metrics across AI tools."
        }
        actions={
          <div>
            <label className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold block mb-1">
              Portfolio
            </label>
            <select
              value={portfolioId}
              onChange={(e) => setPortfolioId(e.target.value)}
              className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm bg-white focus:outline-none focus:border-brand-500 hover:border-slate-400 transition"
            >
              <option value="">All portfolios</option>
              {portfolioList.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
        }
      />

      {summary && (
        <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <KPI
            label="Active users %"
            value={`${summary.active_pct}%`}
            sub={`${summary.active_users} of ${summary.total_resources}`}
            icon={<Gauge size={18} />}
            accent="from-emerald-500 to-teal-500"
          />
          <KPI
            label="Active users"
            value={summary.active_users}
            sub="Active or embedded"
            icon={<Users size={18} />}
            accent="from-brand-500 to-cyan-500"
          />
          <KPI
            label="Tools tracked"
            value={summary.tools_tracked}
            sub="In scope"
            icon={<Wrench size={18} />}
            accent="from-violet-500 to-fuchsia-500"
          />
          <KPI
            label="Avg stage score"
            value={summary.avg_stage_score}
            sub="0 piloting → 4 embedded"
            icon={<Sparkles size={18} />}
            accent="from-amber-500 to-orange-500"
          />
        </section>
      )}

      <Panel title="Heat map" subtitle="Teams × tools, colored by adoption stage">
        <AdoptionHeatMap cells={asArray(heatmap)} />
      </Panel>

      <Panel title="Tools" subtitle={`${asArray(tools).length} in registry`}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {asArray(tools).map((t: any) => <ToolCard key={t.id} tool={t} />)}
        </div>
      </Panel>

      <Panel title="Usage trends (30 days)" subtitle="Daily session count by tool">
        <TrendChart points={asArray(trends)} />
      </Panel>
    </div>
  );
}

function Panel({
  title, subtitle, children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex items-baseline justify-between mb-4">
        <h2 className="font-semibold text-slate-900">{title}</h2>
        {subtitle && <span className="text-xs text-slate-500">{subtitle}</span>}
      </div>
      {children}
    </div>
  );
}
