import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { fetchPortfoliosSummary } from "@/api/hierarchy";
import { asArray } from "@/utils/array";
import { Briefcase, Users, FolderTree, Award, ArrowRight } from "lucide-react";
import { KPI } from "@/components/shared/KPI";
import { PageHeader } from "@/components/shared/PageHeader";

interface PortfolioSummary {
  id: string;
  name: string;
  description?: string;
  team_count: number;
  resource_count: number;
  top_skills: { skill: string; count: number }[];
}

const ACCENTS = [
  "from-brand-500 to-cyan-500",
  "from-violet-500 to-fuchsia-500",
  "from-emerald-500 to-teal-500",
  "from-amber-500 to-orange-500",
  "from-rose-500 to-pink-500",
  "from-indigo-500 to-blue-500",
];

export function PortfoliosPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["portfolios-summary"],
    queryFn: fetchPortfoliosSummary,
  });

  const portfolios = asArray<PortfolioSummary>(data);
  const totalResources = portfolios.reduce((a, p) => a + p.resource_count, 0);
  const totalTeams = portfolios.reduce((a, p) => a + p.team_count, 0);
  const totalSkills = new Set(
    portfolios.flatMap((p) => p.top_skills.map((s) => s.skill))
  ).size;

  return (
    <div className="space-y-6">
      <PageHeader
        kicker="Account dashboard"
        title="Portfolios"
        subtitle="Each portfolio with its resource footprint, team makeup, and skills."
      />

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPI
          label="Portfolios"
          value={portfolios.length}
          sub="Active in account"
          icon={<Briefcase size={18} />}
          accent="from-brand-500 to-cyan-500"
        />
        <KPI
          label="Teams"
          value={totalTeams}
          sub="Across all portfolios"
          icon={<FolderTree size={18} />}
          accent="from-violet-500 to-fuchsia-500"
        />
        <KPI
          label="Resources"
          value={totalResources}
          sub="Active members"
          icon={<Users size={18} />}
          accent="from-emerald-500 to-teal-500"
        />
        <KPI
          label="Distinct top skills"
          value={totalSkills}
          sub="Across portfolios"
          icon={<Award size={18} />}
          accent="from-amber-500 to-orange-500"
        />
      </section>

      {isLoading && <div className="text-slate-500">Loading…</div>}

      {!isLoading && portfolios.length === 0 && (
        <div className="rounded-xl border-2 border-dashed border-slate-300 bg-white p-12 text-center">
          <Briefcase size={36} className="mx-auto text-slate-400 mb-3" />
          <div className="font-semibold text-slate-800 text-lg">No portfolios yet</div>
          <div className="text-sm text-slate-500 mt-1">
            Import projects with a portfolio column to populate this view.
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {portfolios.map((p, i) => (
          <PortfolioCard key={p.id} portfolio={p} accent={ACCENTS[i % ACCENTS.length]} />
        ))}
      </div>
    </div>
  );
}

function PortfolioCard({
  portfolio: p, accent,
}: { portfolio: PortfolioSummary; accent: string }) {
  return (
    <Link
      to="/portfolios/$portfolioId"
      params={{ portfolioId: p.id }}
      className="group block rounded-xl border border-slate-200 bg-white hover:shadow-md hover:border-slate-300 transition overflow-hidden"
    >
      <div className={`h-1 bg-gradient-to-r ${accent}`} aria-hidden />

      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="min-w-0">
            <div className="font-semibold text-slate-900 text-lg group-hover:text-brand-600 transition">
              {p.name}
            </div>
            {p.description && (
              <div className="text-sm text-slate-600 mt-1 line-clamp-2">{p.description}</div>
            )}
          </div>
          <div className={`bg-gradient-to-br ${accent} text-white rounded-lg p-2 shrink-0`}>
            <Briefcase size={18} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <Stat icon={<FolderTree size={14} />} label="Teams" value={p.team_count} />
          <Stat icon={<Users size={14} />} label="Resources" value={p.resource_count} />
        </div>

        {p.top_skills.length > 0 && (
          <div>
            <div className="text-[11px] uppercase tracking-wider text-slate-500 font-semibold mb-1.5">
              Top skills
            </div>
            <div className="flex flex-wrap gap-1.5">
              {p.top_skills.map((s) => (
                <span
                  key={s.skill}
                  className="text-xs bg-slate-100 hover:bg-slate-200 transition text-slate-700 rounded-md px-2 py-0.5"
                >
                  {s.skill}
                  <span className="ml-1 text-slate-400">·{s.count}</span>
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center justify-end mt-4 text-sm text-slate-400 group-hover:text-brand-600 transition">
          View details <ArrowRight size={14} className="ml-1" />
        </div>
      </div>
    </Link>
  );
}

function Stat({
  icon, label, value,
}: { icon: React.ReactNode; label: string; value: number }) {
  return (
    <div className="bg-slate-50 rounded-lg p-2.5">
      <div className="text-xs text-slate-500 flex items-center gap-1.5">
        {icon}
        {label}
      </div>
      <div className="text-xl font-bold text-slate-900 mt-0.5">{value}</div>
    </div>
  );
}
