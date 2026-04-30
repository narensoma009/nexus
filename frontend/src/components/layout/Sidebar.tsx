import { Link } from "@tanstack/react-router";
import {
  LayoutDashboard, Sparkles, Presentation, MessageSquare,
  Settings, Briefcase, Zap,
} from "lucide-react";

const PRIMARY = [
  { to: "/", label: "Programs", icon: LayoutDashboard },
  { to: "/portfolios", label: "Portfolios", icon: Briefcase },
  { to: "/ai-adoption", label: "AI Adoption", icon: Sparkles },
];

const TOOLS = [
  { to: "/slides", label: "Presentations", icon: Presentation },
  { to: "/chat", label: "Ask Nexus", icon: MessageSquare },
];

const SETTINGS = [{ to: "/admin", label: "Admin", icon: Settings }];

export function Sidebar() {
  return (
    <aside className="w-60 shrink-0 border-r border-slate-200 bg-white flex flex-col">
      <div className="px-4 py-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-brand-500 to-violet-500 grid place-items-center">
            <Zap size={18} className="text-white" />
          </div>
          <div>
            <div className="font-bold text-slate-900 text-lg leading-tight">Nexus</div>
            <div className="text-xs text-slate-500 leading-tight">AT&amp;T account</div>
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-5">
        <Section label="Workspace" items={PRIMARY} />
        <Section label="Tools" items={TOOLS} />
        <Section label="System" items={SETTINGS} />
      </nav>

      <div className="p-3 border-t border-slate-200 text-xs text-slate-400">
        v0.1 · build {new Date().getFullYear()}
      </div>
    </aside>
  );
}

function Section({
  label, items,
}: {
  label: string;
  items: { to: string; label: string; icon: React.ElementType }[];
}) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-wider font-semibold text-slate-400 px-2 mb-1.5">
        {label}
      </div>
      <div className="space-y-0.5">
        {items.map((n) => (
          <Link
            key={n.to}
            to={n.to}
            className="flex items-center gap-2.5 rounded-lg px-2.5 py-2 text-sm text-slate-700 hover:bg-slate-100 transition [&.active]:bg-gradient-to-r [&.active]:from-brand-500 [&.active]:to-cyan-500 [&.active]:text-white [&.active]:shadow-sm"
            activeProps={{ className: "active" }}
          >
            <n.icon size={16} />
            {n.label}
          </Link>
        ))}
      </div>
    </div>
  );
}
