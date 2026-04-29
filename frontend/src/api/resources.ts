import { api } from "./client";

export const fetchResources = (params?: { team_id?: string; page?: number; page_size?: number }) =>
  api.get("/api/resources", { params }).then((r) => r.data);
export const fetchResource = (id: string) => api.get(`/api/resources/${id}`).then((r) => r.data);
export const fetchResourceAssignments = (id: string) =>
  api.get(`/api/resources/${id}/assignments`).then((r) => r.data);
export const bulkImportResources = (file: File) => {
  const fd = new FormData();
  fd.append("file", file);
  return api.post("/api/resources/bulk-import", fd, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then((r) => r.data);
};
