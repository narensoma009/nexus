import { useParams } from "@tanstack/react-router";
import { usePortfolio, usePortfolioTeams } from "@/hooks/useHierarchyNode";
import { Breadcrumb } from "@/components/layout/Breadcrumb";
import { NodeCard } from "@/components/hierarchy/NodeCard";

export function PortfolioPage() {
  const { portfolioId } = useParams({ from: "/portfolios/$portfolioId" });
  const { data: portfolio } = usePortfolio(portfolioId);
  const { data: teams } = usePortfolioTeams(portfolioId);

  if (!portfolio) return <div className="text-slate-500">Loading…</div>;

  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: "Portfolios" }, { label: portfolio.name }]} />
      <h1 className="text-2xl font-semibold">{portfolio.name}</h1>
      {portfolio.description && <p className="text-slate-600">{portfolio.description}</p>}

      <section>
        <h2 className="font-semibold mb-2">Teams</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {(teams ?? []).map((t: any) => (
            <NodeCard key={t.id} title={t.name} subtitle="Team" />
          ))}
        </div>
      </section>
    </div>
  );
}
