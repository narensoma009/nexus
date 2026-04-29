import { Sidebar } from "./Sidebar";
import { ChatPanel } from "../chat/ChatPanel";
import { useState } from "react";
import { MessageSquare } from "lucide-react";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [chatOpen, setChatOpen] = useState(false);
  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">{children}</main>

      <button
        onClick={() => setChatOpen(true)}
        className="fixed bottom-5 right-5 bg-brand-500 hover:bg-brand-600 text-white rounded-full p-3 shadow-lg"
        aria-label="Open assistant"
      >
        <MessageSquare size={20} />
      </button>

      {chatOpen && <ChatPanel onClose={() => setChatOpen(false)} />}
    </div>
  );
}
