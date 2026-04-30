import { useParams, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  fetchPortfolioStats, fetchPortfolioAIHeatmap, fetchPortfolioAITrends,
} from "@/api/hierarchy";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { Users, FolderTree, Sparkles, Award, ArrowRight } from "lucide-react";
import { AdoptionHeatMap } from "@/components/ai-adoption/AdoptionHeatMap";
import { TrendChart } from "@/components/ai-adoption/TrendChart";
import { KPI } from "@/components/shared/KPI";
import { asArray } from "@/utils/array";

const STAGE_COLOR: Record<string, string> = {
  piloting: "bg-slate-300",
  onboarded: "bg-sky-400",
  active: "bg-teal-500",
  embedded: "bg-emerald-600",
};

interface Stats {
  id: string;
  name: string;
  description?: string;
  team_count: number;
  resource_count: number;
  roles: { role: string; count: number }[];
  seniority: { level: string; count: number }[];
  skills: { skill: string; count: number }[];
  ai_adoption: {
    total_licenses: number;
    by_stage: Record<string, number>;
    by_tool: {
      tool_id: string;
      name: string;
      vendor: string;
      stages: Record<string, number>;
      total: number;
    }[];
  };
}

export function PortfolioPage() {
  const { portfolioId } = useParams({ from: "/portfolios/$portfolioId" });
  const { data, isLoading } = useQuery<Stats>({
    queryKey: ["portfolio-stats", portfolioId],
    queryFn: () => fetchPortfolioStats(portfolioId),
  });
  const { data: heatmap } = useQuery({
    queryKey: ["portfolio-ai-heatmap", portfolioId],
    queryFn: () => fetchPortfolioAIHeatmap(portfolioId),
  });
  const { data: trends } = useQuery({
    queryKey: ["portfolio-ai-trends", portfolioId],
    queryFn: () => fetchPortfolioAITrends(portfolioId),
  });

  if (isLoading || !data) return <div className="text-slate-500">Loading…</div>;

  const maxRole = Math.max(1, ...data.roles.map((r) => r.count));
  const maxSkill = Math.max(1, ...data.skills.map((s) => s.count));
  const adoptionRate = data.resource_count
    ? Math.round((data.ai_adoption.total_licenses / data.resource_count) * 100)
    : 0;

  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: "Portfolios", to: "/portfolios" }, { label: data.name }]} />

      <header className="rounded-xl border border-slate-200 bg-gradient-to-br from-white to-slate-50 p-6">
        <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">
          Portfolio
        </div>
        <h1 className="text-3xl font-bold text-slate-900 mt-1">{data.name}</h1>
        {data.description && (
          <p className="text-slate-600 mt-1.5 max-w-3xl">{data.description}</p>
        )}
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPI
          label="Teams" value={data.team_count}
          sub="Including sub-teams"
          icon={<FolderTree size={18} />}
          accent="from-violet-500 to-fuchsia-500"
        />
        <KPI
          label="Resources" value={data.resource_count}
          sub="Active members"
          icon={<Users size={18} />}
          accent="from-emerald-500 to-teal-500"
        />
        <KPI
          label="AI licenses" value={data.ai_adoption.total_licenses}
          sub={`${adoptionRate}% adoption`}
          icon={<Sparkles size={18} />}
          accent="from-amber-500 to-orange-500"
        />
        <KPI
          label="Skills tracked" value={data.skills.length}
          sub="Distinct technologies"
          icon={<Award size={18} />}
          accent="from-brand-500 to-cyan-500"
        />
      </section>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Panel title="Tech skills" subtitle={`${data.skills.length} distinct`}>
          {data.skills.length === 0 ? <Empty /> : (
            <div className="space-y-1.5">
              {data.skills.slice(0, 12).map((s) => (
                <BarRow
                  key={s.skill}
                  label={s.skill}
                  value={s.count}
                  max={maxSkill}
                  gradient="from-cyan-400 to-brand-500"
                />
              ))}
            </div>
          )}
        </Panel>

        <Panel title="Roles" subtitle={`${data.roles.length} unique`}>
          {data.roles.length === 0 ? <Empty /> : (
            <div className="space-y-1.5">
              {data.roles.slice(0, 12).map((r) => (
                <BarRow
                  key={r.role}
                  label={r.role}
                  value={r.count}
                  max={maxRole}
                  gradient="from-violet-400 to-fuchsia-500"
                />
              ))}
            </div>
          )}
        </Panel>

        <Panel title="Seniority distribution">
          {data.seniority.length === 0 ? <Empty /> : (
            <div className="grid grid-cols-4 gap-3">
              {data.seniority.map((s) => (
                <div key={s.level} className="rounded-lg bg-slate-50 p-3 text-center">
                  <div className="text-3xl font-bold text-slate-900">{s.count}</div>
                  <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold mt-1">
                    {s.level}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Panel>

        <Panel title="AI adoption breakdown" subtitle={`${data.ai_adoption.total_licenses} licenses`}>
          {data.ai_adoption.total_licenses === 0 ? <Empty /> : (
            <div className="space-y-3">
              <StageLegend />
              {data.ai_adoption.by_tool.map((t) => (
                <ToolStageBar key={t.tool_id} tool={t} />
              ))}
            </div>
          )}
        </Panel>
      </div>

      <Panel title="AI heat map (teams × tools)" subtitle={`${asArray(heatmap).length} cells`}>
        <AdoptionHeatMap cells={asArray(heatmap)} />
      </Panel>

      <Panel title="Usage trends (30 days)">
        <TrendChart points={asArray(trends)} />
      </Panel>

      <Link
        to="/ai-adoption"
        className="inline-flex items-center gap-1 text-sm text-brand-600 hover:text-brand-700 font-medium"
      >
        Open full AI adoption dashboard <ArrowRight size={14} />
      </Link>
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

function Empty() {
  return <div className="text-sm text-slate-400 italic py-6 text-center">No data</div>;
}

function BarRow({
  label, value, max, gradient,
}: { label: string; value: number; max: number; gradient: string }) {
  const pct = (value / max) * 100;
  return (
    <div className="flex items-center gap-3 text-xs">
      <div className="w-32 truncate text-slate-700">{label}</div>
      <div className="flex-1 bg-slate-100 rounded-full h-2 relative overflow-hidden">
        <div
          className={`bg-gradient-to-r ${gradient} h-full rounded-full`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="w-8 text-right tabular-nums font-semibold text-slate-700">{value}</div>
    </div>
  );
}

function StageLegend() {
  return (
    <div className="flex gap-3 text-xs text-slate-600 flex-wrap pb-2 border-b border-slate-100">
      {Object.entries(STAGE_COLOR).map(([stage, color]) => (
        <div key={stage} className="flex items-center gap-1.5">
          <span className={`w-2.5 h-2.5 rounded-sm ${color}`} />
          {stage}
        </div>
      ))}
    </div>
  );
}

function ToolStageBar({
  tool,
}: {
  tool: { name: string; vendor: string; stages: Record<string, number>; total: number };
}) {
  const order = ["piloting", "onboarded", "active", "embedded"];
  return (
    <div>
      <div className="flex items-center justify-between text-xs mb-1.5">
        <span>
          <span className="font-medium text-slate-800">{tool.name}</span>
          <span className="text-slate-400 font-normal ml-1.5">{tool.vendor}</span>
        </span>
        <span className="text-slate-500 tabular-nums">{tool.total}</span>
      </div>
      <div className="flex h-3 rounded-full overflow-hidden bg-slate-100">
        {order.map((stage) => {
          const count = tool.stages[stage] ?? 0;
          const pct = tool.total ? (count / tool.total) * 100 : 0;
          if (pct === 0) return null;
          return (
            <div
              key={stage}
              className={STAGE_COLOR[stage]}
              style={{ width: `${pct}%` }}
              title={`${stage}: ${count}`}
            />
          );
        })}
      </div>
    </div>
  );
}
