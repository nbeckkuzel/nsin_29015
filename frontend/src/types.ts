// Typy odpowiadające modelom z backendu (app/models.py).

export type Status = "urgent" | "progress" | "stale";
export type Priority = "high" | "medium" | "low";

export interface Task {
  id: string;
  raw_text: string;
  source_image: string | null;
  title: string;
  label: string;
  created_date: string;
  status: Status;
  ai_priority: Priority;
  ai_reasoning: string;
  alive: boolean;
  closed_at: string | null;
  age_days: number;
}

export interface BurndownPoint {
  date: string;
  remaining: number;
  closed_today: number;
}

export interface DashboardState {
  tasks: Task[];
  burndown: BurndownPoint[];
  labels: string[];
}

export interface ChatResponse {
  answer: string;
  sources: string[];
}
