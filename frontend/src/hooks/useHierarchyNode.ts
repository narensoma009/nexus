import { useQuery } from "@tanstack/react-query";
import { fetchTree, fetchPortfolio, fetchPortfolioTeams, fetchTeam, fetchTeamMembers } from "@/api/hierarchy";

export const useTree = () => useQuery({ queryKey: ["hierarchy", "tree"], queryFn: fetchTree });
export const usePortfolio = (id: string) =>
  useQuery({ queryKey: ["portfolio", id], queryFn: () => fetchPortfolio(id), enabled: !!id });
export const usePortfolioTeams = (id: string) =>
  useQuery({ queryKey: ["portfolio", id, "teams"], queryFn: () => fetchPortfolioTeams(id), enabled: !!id });
export const useTeam = (id: string) =>
  useQuery({ queryKey: ["team", id], queryFn: () => fetchTeam(id), enabled: !!id });
export const useTeamMembers = (id: string) =>
  useQuery({ queryKey: ["team", id, "members"], queryFn: () => fetchTeamMembers(id), enabled: !!id });
