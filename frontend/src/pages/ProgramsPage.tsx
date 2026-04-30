import { useQuery } from "@tanstack/react-query";
import { Link } from "@tanstack/react-router";
import { fetchProgramsWithProjects } from "@/api/programs";
import { fetchPortfoliosSummary } from "@/api/hierarchy";
import { fetchSummary } from "@/api/aiAdoption";
import { StatusBadge } from "@/components/shared/StatusBadge";
import { asArray } from "@/utils/array";
import {
  Briefcase, Users, FolderTree, Sparkles, TrendingUp, AlertTriangle,
  CheckCircle2, Clock, ArrowRight, Upload,
} from "lucide-react";

interface ProgramWithProjects {
  id: string;
  name: string;
  description?: string;
  status: string;
  project_count: number;
  projects: { id: string; name: string; status: string }[];
}

export function ProgramsPage() {
  const programsQ = useQuery({
    queryKey: ["programs-with-projects"],
    queryFn: fetchProgramsWithProjects,
  });
  const portfoliosQ = useQuery({
    queryKey: ["portfolios-summary"],
    queryFn: fetchPortfoliosSummary,
  });
  const adoptionQ = useQuery({
    queryKey: ["adoption-summary"],
    queryFn: () => fetchSummary(),
  });

  const programs = asArray<ProgramWithProjects>(programsQ.data);
  const portfolios = asArray<{ resource_count: number; team_count: number }>(portfoliosQ.data);

  const totalResources = portfolios.reduce((a, p) => a + p.resource_count, 0);
  const totalTeams = portfolios.reduce((a, p) => a + p.team_count, 0);

  return (
    <div className="space-y-6">
      <header>
        <div className="flex items-end justify-between gap-4 flex-wrap">
          <div>
            <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">
              Account dashboard
            </div>
            <h1 className="text-3xl font-bold text-slate-900 mt-1">Programs</h1>
            <p className="text-slate-600 text-sm mt-1">
              Cross-portfolio view of every active program and its projects.
            </p>
          </div>
          <Link
            to="/admin"
            className="inline-flex items-center gap-1.5 text-sm text-brand-600 hover:text-brand-700 font-medium"
          >
            <Upload size={14} /> Import projects
          </Link>
        </div>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPI
          label="Programs"
          value={programs.length}
          sub={`${programs.reduce((a, p) => a + p.project_count, 0)} projects`}
          icon={<TrendingUp size={18} />}
          accent="from-brand-500 to-cyan-500"
        />
        <KPI
          label="Portfolios"
          value={portfolios.length}
          sub={`${totalTeams} teams`}
          icon={<Briefcase size={18} />}
          accent="from-violet-500 to-fuchsia-500"
        />
        <KPI
          label="Resources"
          value={totalResources}
          sub="Active platform members"
          icon={<Users size={18} />}
          accent="from-emerald-500 to-teal-500"
        />
        <KPI
          label="AI active users"
          value={adoptionQ.data?.active_users ?? 0}
          sub={`${adoptionQ.data?.active_pct ?? 0}% of org`}
          icon={<Sparkles size={18} />}
          accent="from-amber-500 to-orange-500"
        />
      </section>

      {programsQ.isLoading && <div className="text-slate-500">Loading…</div>}

      {!programsQ.isLoading && programs.length === 0 && (
        <div className="rounded-xl border-2 border-dashed border-slate-300 bg-white p-12 text-center">
          <Upload size={36} className="mx-auto text-slate-400 mb-3" />
          <div className="font-semibold text-slate-800 text-lg">No programs yet</div>
          <div className="text-sm text-slate-500 mt-1 max-w-md mx-auto">
            Upload your project spreadsheet to get started — projects will be auto-categorized into programs.
          </div>
          <Link
            to="/admin"
            className="inline-flex items-center gap-1.5 mt-5 bg-brand-500 hover:bg-brand-600 text-white text-sm rounded-lg px-4 py-2 font-medium"
          >
            <Upload size={14} /> Go to Admin → Import projects
          </Link>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {programs.map((p) => (
          <ProgramCard key={p.id} program={p} />
        ))}
      </div>
    </div>
  );
}

function ProgramCard({ program }: { program: ProgramWithProjects }) {
  const onTrack = program.projects.filter((p) => p.status === "on_track").length;
  const atRisk = program.projects.filter((p) => p.status === "at_risk").length;
  const completed = program.projects.filter((p) => p.status === "completed").length;
  const total = program.projects.length;

  return (
    <Link
      to="/programs/$programId"
      params={{ programId: program.id }}
      className="group block rounded-xl border border-slate-200 bg-white hover:shadow-md hover:border-slate-300 transition overflow-hidden"
    >
      <div className="p-5 border-b border-slate-100">
        <div className="min-w-0">
          <div className="font-semibold text-slate-900 text-lg group-hover:text-brand-600 transition">
            {program.name}
          </div>
          {program.description && (
            <div className="text-sm text-slate-600 mt-1 line-clamp-2">{program.description}</div>
          )}
        </div>

        {total > 0 && (
          <div className="mt-4 space-y-1.5">
            <div className="flex items-center justify-between text-xs text-slate-500">
              <span>{total} projects</span>
              <span className="flex items-center gap-3">
                {onTrack > 0 && (
                  <span className="flex items-center gap-1 text-emerald-700">
                    <CheckCircle2 size={12} /> {onTrack}
                  </span>
                )}
                {atRisk > 0 && (
                  <span className="flex items-center gap-1 text-amber-700">
                    <AlertTriangle size={12} /> {atRisk}
                  </span>
                )}
                {completed > 0 && (
                  <span className="flex items-center gap-1 text-slate-500">
                    <Clock size={12} /> {completed}
                  </span>
                )}
              </span>
            </div>
            <div className="flex h-1.5 rounded-full overflow-hidden bg-slate-100">
              {onTrack > 0 && (
                <div className="bg-emerald-500" style={{ width: `${(onTrack / total) * 100}%` }} />
              )}
              {atRisk > 0 && (
                <div className="bg-amber-500" style={{ width: `${(atRisk / total) * 100}%` }} />
              )}
              {completed > 0 && (
                <div className="bg-slate-400" style={{ width: `${(completed / total) * 100}%` }} />
              )}
            </div>
          </div>
        )}
      </div>

      {program.projects.length > 0 && (
        <ul className="bg-slate-50/50 divide-y divide-slate-100">
          {program.projects.slice(0, 4).map((proj) => (
            <li
              key={proj.id}
              className="px-5 py-2 flex items-center justify-between text-sm"
            >
              <span className="text-slate-700 truncate">{proj.name}</span>
              <StatusBadge status={proj.status} />
            </li>
          ))}
          {program.projects.length > 4 && (
            <li className="px-5 py-2 text-xs text-slate-500 flex items-center justify-between">
              <span>+ {program.projects.length - 4} more projects</span>
              <ArrowRight size={12} className="text-slate-400 group-hover:text-brand-500" />
            </li>
          )}
        </ul>
      )}
    </Link>
  );
}

function KPI({
  label, value, sub, icon, accent,
}: {
  label: string;
  value: number | string;
  sub?: string;
  icon: React.ReactNode;
  accent: string;
}) {
  return (
    <div className="relative rounded-xl border border-slate-200 bg-white p-4 overflow-hidden">
      <div
        className={`absolute inset-y-0 left-0 w-1 bg-gradient-to-b ${accent}`}
        aria-hidden
      />
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs uppercase tracking-wider text-slate-500 font-medium">
            {label}
          </div>
          <div className="text-3xl font-bold text-slate-900 mt-1">{value}</div>
          {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
        </div>
        <div className={`bg-gradient-to-br ${accent} text-white rounded-lg p-2`}>{icon}</div>
      </div>
    </div>
  );
}
