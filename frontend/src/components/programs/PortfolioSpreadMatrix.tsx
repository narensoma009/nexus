import { Link } from "@tanstack/react-router";
import type { PortfolioSpreadEntry } from "@/types";

export function PortfolioSpreadMatrix({
  entries,
}: {
  entries: PortfolioSpreadEntry[];
}) {
  if (!entries.length) return <div className="text-sm text-slate-500">No spread data.</div>;
  return (
    <div className="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-3 py-2 text-left font-medium text-slate-600">Portfolio</th>
            <th className="px-3 py-2 text-right font-medium text-slate-600">Teams</th>
            <th className="px-3 py-2 text-right font-medium text-slate-600">Resources</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {entries.map((e) => (
            <tr key={e.portfolio_id} className="hover:bg-slate-50">
              <td className="px-3 py-2">
                <Link
                  to="/portfolios/$portfolioId"
                  params={{ portfolioId: e.portfolio_id }}
                  className="text-brand-600 hover:underline"
                >
                  {e.portfolio_name}
                </Link>
              </td>
              <td className="px-3 py-2 text-right">{e.team_count}</td>
              <td className="px-3 py-2 text-right">{e.resource_count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
