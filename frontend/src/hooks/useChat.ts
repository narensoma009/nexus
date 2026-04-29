import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { sendChatMessage } from "@/api/chat";

export function useChat(context?: Record<string, any>) {
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);

  const send = useMutation({
    mutationFn: (msg: string) =>
      sendChatMessage({ message: msg, session_id: sessionId, context }),
    onSuccess: (data) => {
      setSessionId(data.session_id);
      setMessages((m) => [...m, { role: "assistant", content: data.reply }]);
    },
  });

  const sendMessage = (msg: string) => {
    setMessages((m) => [...m, { role: "user", content: msg }]);
    send.mutate(msg);
  };

  return { messages, sendMessage, isPending: send.isPending };
}
