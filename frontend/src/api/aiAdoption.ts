import { api } from "./client";

const params = (portfolioId?: string) =>
  portfolioId ? { portfolio_id: portfolioId } : {};

export const fetchTools = (portfolioId?: string) =>
  api.get("/api/ai-adoption/tools", { params: params(portfolioId) }).then((r) => r.data);

export const fetchSummary = (portfolioId?: string) =>
  api.get("/api/ai-adoption/summary", { params: params(portfolioId) }).then((r) => r.data);

export const fetchHeatmap = (portfolioId?: string) =>
  api.get("/api/ai-adoption/heatmap", { params: params(portfolioId) }).then((r) => r.data);

export const fetchTrends = (portfolioId?: string) =>
  api.get("/api/ai-adoption/trends", { params: params(portfolioId) }).then((r) => r.data);
