import { api } from "./client";

export const sendChatMessage = (payload: {
  message: string;
  session_id?: string;
  context?: Record<string, any>;
}) => api.post("/api/chat/message", payload).then((r) => r.data);

export const fetchSessions = () => api.get("/api/chat/sessions").then((r) => r.data);
