import { api } from "./client";

export const fetchTools = () => api.get("/api/ai-adoption/tools").then((r) => r.data);
export const fetchSummary = () => api.get("/api/ai-adoption/summary").then((r) => r.data);
export const fetchHeatmap = () => api.get("/api/ai-adoption/heatmap").then((r) => r.data);
export const fetchTrends = () => api.get("/api/ai-adoption/trends").then((r) => r.data);
