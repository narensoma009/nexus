import axios from "axios";
import { acquireToken } from "@/auth/AuthProvider";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

api.interceptors.request.use(async (config) => {
  const token = await acquireToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
