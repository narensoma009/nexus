import { Search, Bell } from "lucide-react";

export function Topbar() {
  return (
    <header className="h-14 border-b border-slate-200 bg-white/80 backdrop-blur sticky top-0 z-30 flex items-center px-6 gap-4">
      <div className="flex-1 flex items-center gap-3 max-w-xl">
        <Search size={16} className="text-slate-400" />
        <input
          placeholder="Search programs, portfolios, resources…"
          className="flex-1 bg-transparent text-sm focus:outline-none placeholder:text-slate-400"
        />
      </div>

      <button
        className="relative text-slate-500 hover:text-slate-800"
        aria-label="Notifications"
      >
        <Bell size={18} />
        <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-rose-500" />
      </button>

      <div className="flex items-center gap-2 pl-3 border-l border-slate-200">
        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-brand-500 to-violet-500 text-white text-sm font-semibold grid place-items-center">
          DU
        </div>
        <div className="text-sm leading-tight hidden md:block">
          <div className="font-medium text-slate-800">Dev User</div>
          <div className="text-xs text-slate-500">Account admin</div>
        </div>
      </div>
    </header>
  );
}
