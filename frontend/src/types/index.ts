export interface Program {
  id: string;
  account_id: string;
  name: string;
  description?: string;
  status: "on_track" | "at_risk" | "planning" | "completed";
  start_date?: string;
  end_date?: string;
}

export interface Portfolio {
  id: string;
  account_id: string;
  name: string;
  description?: string;
}

export interface Team {
  id: string;
  name: string;
  portfolio_id?: string;
  sub_portfolio_id?: string;
  parent_team_id?: string;
}

export interface Resource {
  id: string;
  team_id: string;
  name: string;
  email: string;
  role: string;
  seniority: string;
  skills?: string;
  is_active: boolean;
}

export interface PortfolioSpreadEntry {
  portfolio_id: string;
  portfolio_name: string;
  team_count: number;
  resource_count: number;
}

export interface AITool {
  id: string;
  name: string;
  vendor: string;
  category: string;
  rollout_date?: string;
  target_user_count?: number;
}

export interface HeatmapCell {
  team_id: string;
  team_name: string;
  tool_id: string;
  tool_name: string;
  stage: string;
  user_count: number;
}

export interface TrendPoint {
  date: string;
  tool_id: string;
  tool_name: string;
  sessions: number;
  active_minutes: number;
}

export interface PPTTemplate {
  id: string;
  name: string;
  tags?: string;
  slide_count: number;
  placeholder_map: string;
  uploaded_by: string;
  uploaded_at: string;
  last_used_at?: string;
}
