import { Link } from "@tanstack/react-router";
import { LayoutDashboard, Sparkles, Presentation, MessageSquare, Settings, Users } from "lucide-react";

const NAV = [
  { to: "/", label: "Programs", icon: LayoutDashboard },
  { to: "/ai-adoption", label: "AI Adoption", icon: Sparkles },
  { to: "/slides", label: "Slides", icon: Presentation },
  { to: "/chat", label: "Assistant", icon: MessageSquare },
  { to: "/admin", label: "Admin", icon: Settings },
];

export function Sidebar() {
  return (
    <aside className="w-56 shrink-0 border-r border-slate-200 bg-white p-3 space-y-1">
      <div className="font-semibold text-brand-600 px-2 py-3 flex items-center gap-2">
        <Users size={18} /> AT&amp;T Platform
      </div>
      {NAV.map((n) => (
        <Link
          key={n.to}
          to={n.to}
          className="flex items-center gap-2 rounded px-2 py-1.5 text-sm text-slate-700 hover:bg-slate-100 [&.active]:bg-brand-500 [&.active]:text-white"
          activeProps={{ className: "active" }}
        >
          <n.icon size={16} />
          {n.label}
        </Link>
      ))}
    </aside>
  );
}
