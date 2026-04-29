import { useChat } from "@/hooks/useChat";
import { useState } from "react";
import { Send } from "lucide-react";

export function ChatPage() {
  const { messages, sendMessage, isPending } = useChat();
  const [input, setInput] = useState("");

  const submit = () => {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  };

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <h1 className="text-2xl font-semibold">Platform Assistant</h1>
      <div className="space-y-3 min-h-[300px]">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`rounded-lg p-3 text-sm ${
              m.role === "user" ? "bg-brand-500 text-white ml-12" : "bg-white border border-slate-200 mr-12"
            }`}
          >
            {m.content}
          </div>
        ))}
        {isPending && <div className="text-xs text-slate-400">Thinking…</div>}
      </div>
      <div className="flex gap-2 sticky bottom-0 bg-slate-50 pt-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Ask about programs, teams, AI adoption…"
          className="flex-1 rounded border border-slate-300 px-3 py-2 text-sm"
        />
        <button
          onClick={submit}
          disabled={isPending}
          className="bg-brand-500 hover:bg-brand-600 text-white rounded px-4"
          aria-label="Send"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
