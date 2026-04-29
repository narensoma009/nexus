import { api } from "./client";

export const fetchTemplates = () => api.get("/api/slides/templates").then((r) => r.data);

export const uploadTemplate = (file: File, name: string, tags: string) => {
  const fd = new FormData();
  fd.append("file", file);
  fd.append("name", name);
  fd.append("tags", tags);
  return api.post("/api/slides/templates", fd).then((r) => r.data);
};

export const generateSlides = (payload: {
  template_id: string;
  program_id?: string;
  period?: string;
  scope?: any;
}) => api.post("/api/slides/generate", payload).then((r) => r.data);

export const fetchJob = (jobId: string) =>
  api.get(`/api/slides/jobs/${jobId}`).then((r) => r.data);

export const downloadJob = (jobId: string) =>
  api.get(`/api/slides/jobs/${jobId}/download`, { responseType: "blob" }).then((r) => r.data);
