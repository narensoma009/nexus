import { api } from "./client";

export const fetchPrograms = () => api.get("/api/programs").then((r) => r.data);
export const fetchProgram = (id: string) => api.get(`/api/programs/${id}`).then((r) => r.data);
export const fetchPortfolioSpread = (id: string) =>
  api.get(`/api/programs/${id}/portfolio-spread`).then((r) => r.data);
export const fetchProgramWorkstreams = (id: string) =>
  api.get(`/api/programs/${id}/workstreams`).then((r) => r.data);
export const fetchProgramResources = (id: string) =>
  api.get(`/api/programs/${id}/resources`).then((r) => r.data);
