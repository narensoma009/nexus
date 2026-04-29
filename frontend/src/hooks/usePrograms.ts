import { useQuery } from "@tanstack/react-query";
import { fetchPrograms, fetchProgram, fetchPortfolioSpread } from "@/api/programs";

export const usePrograms = () =>
  useQuery({ queryKey: ["programs"], queryFn: fetchPrograms });

export const useProgram = (id: string) =>
  useQuery({ queryKey: ["program", id], queryFn: () => fetchProgram(id), enabled: !!id });

export const usePortfolioSpread = (id: string) =>
  useQuery({ queryKey: ["program", id, "spread"], queryFn: () => fetchPortfolioSpread(id), enabled: !!id });
