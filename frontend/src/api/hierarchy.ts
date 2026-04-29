import { api } from "./client";

export const fetchTree = () => api.get("/api/hierarchy/tree").then((r) => r.data);
export const fetchPortfolios = () => api.get("/api/hierarchy/portfolios").then((r) => r.data);
export const fetchPortfolio = (id: string) =>
  api.get(`/api/hierarchy/portfolios/${id}`).then((r) => r.data);
export const fetchPortfolioTeams = (id: string) =>
  api.get(`/api/hierarchy/portfolios/${id}/teams`).then((r) => r.data);
export const fetchTeam = (id: string) => api.get(`/api/hierarchy/teams/${id}`).then((r) => r.data);
export const fetchTeamMembers = (id: string) =>
  api.get(`/api/hierarchy/teams/${id}/members`).then((r) => r.data);
