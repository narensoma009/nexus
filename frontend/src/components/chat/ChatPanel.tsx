import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { sendChatMessage } from "@/api/chat";
import { X, Send } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export function ChatPanel({
  onClose,
  context,
}: {
  onClose: () => void;
  context?: Record<string, any>;
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>();

  const send = useMutation({
    mutationFn: (msg: string) =>
      sendChatMessage({ message: msg, session_id: sessionId, context }),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
    },
    onError: (err: any) => {
      setMessages((m) => [...m, { role: "assistant", content: `Error: ${err.message}` }]);
    },
  });

  const submit = () => {
    if (!input.trim()) return;
    setMessages((m) => [...m, { role: "user", content: input }]);
    send.mutate(input);
    setInput("");
  };

  return (
    <div className="fixed top-0 right-0 h-full w-96 bg-white border-l border-slate-200 shadow-xl flex flex-col z-50">
      <div className="flex items-center justify-between p-3 border-b border-slate-200">
        <div className="font-semibold">Ask Nexus</div>
        <button onClick={onClose} aria-label="Close" className="text-slate-500 hover:text-slate-800">
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-auto p-3 space-y-3">
        {messages.length === 0 && (
          <div className="text-sm text-slate-500">
            Ask about programs, teams, AI adoption, or utilization.
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`text-sm rounded-lg p-2 ${
              m.role === "user" ? "bg-brand-500 text-white ml-8" : "bg-slate-100 text-slate-900 mr-8"
            }`}
          >
            {m.content}
          </div>
        ))}
        {send.isPending && <div className="text-xs text-slate-400">Thinking...</div>}
      </div>

      <div className="p-3 border-t border-slate-200 flex gap-2">
        <input
          className="flex-1 rounded border border-slate-300 px-3 py-1.5 text-sm focus:outline-none focus:border-brand-500"
          placeholder="Ask anything..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
        />
        <button
          onClick={submit}
          disabled={send.isPending}
          className="bg-brand-500 hover:bg-brand-600 text-white rounded px-3"
          aria-label="Send"
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
