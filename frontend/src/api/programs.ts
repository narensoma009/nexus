import { api } from "./client";

export const fetchPrograms = () => api.get("/api/programs").then((r) => r.data);
export const fetchProgramsWithProjects = () =>
  api.get("/api/programs-with-projects").then((r) => r.data);

export const bulkImportProjects = (file: File) => {
  const fd = new FormData();
  fd.append("file", file);
  return api.post("/api/programs/bulk-import-projects", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then((r) => r.data);
};

export const reloadCategorizationRules = () =>
  api.post("/api/programs/reload-categorization-rules").then((r) => r.data);
export const fetchProgram = (id: string) => api.get(`/api/programs/${id}`).then((r) => r.data);
export const fetchPortfolioSpread = (id: string) =>
  api.get(`/api/programs/${id}/portfolio-spread`).then((r) => r.data);
export const fetchProgramWorkstreams = (id: string) =>
  api.get(`/api/programs/${id}/workstreams`).then((r) => r.data);
export const fetchProgramResources = (id: string) =>
  api.get(`/api/programs/${id}/resources`).then((r) => r.data);
