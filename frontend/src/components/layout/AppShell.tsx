import { Sidebar } from "./Sidebar";
import { Topbar } from "./Topbar";
import { ChatPanel } from "../chat/ChatPanel";
import { useState } from "react";
import { MessageSquare } from "lucide-react";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [chatOpen, setChatOpen] = useState(false);
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar />
        <main className="flex-1 overflow-auto p-6 lg:p-8 max-w-[1600px] w-full mx-auto">
          {children}
        </main>
      </div>

      <button
        onClick={() => setChatOpen(true)}
        className="fixed bottom-6 right-6 bg-gradient-to-br from-brand-500 to-violet-500 hover:from-brand-600 hover:to-violet-600 text-white rounded-full p-3.5 shadow-lg shadow-brand-500/30 transition hover:scale-105"
        aria-label="Ask Nexus"
      >
        <MessageSquare size={20} />
      </button>

      {chatOpen && <ChatPanel onClose={() => setChatOpen(false)} />}
    </div>
  );
}
