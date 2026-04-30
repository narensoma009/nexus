import axios from "axios";
import { acquireToken } from "@/auth/AuthProvider";

const apiBase =
  import.meta.env.VITE_API_BASE_URL ||
  (import.meta.env.DEV ? "http://localhost:8000" : "");

export const api = axios.create({
  baseURL: apiBase,
});

api.interceptors.request.use(async (config) => {
  const token = await acquireToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
