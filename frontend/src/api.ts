// Warstwa komunikacji z backendem FastAPI.
import type { ChatResponse, DashboardState } from "./types";

const BASE = "http://localhost:8000";

export async function fetchTasks(): Promise<DashboardState> {
  const res = await fetch(`${BASE}/tasks`);
  if (!res.ok) throw new Error(`GET /tasks: ${res.status}`);
  return res.json();
}

export async function importScreenshots(files: File[]): Promise<DashboardState> {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));
  const res = await fetch(`${BASE}/import`, { method: "POST", body: form });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`POST /import: ${res.status} — ${detail}`);
  }
  return res.json();
}

export async function closeTask(taskId: string): Promise<void> {
  const res = await fetch(`${BASE}/tasks/${taskId}/close`, { method: "PATCH" });
  if (!res.ok) throw new Error(`PATCH close: ${res.status}`);
}

export async function sendChat(message: string): Promise<ChatResponse> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`POST /chat: ${res.status} — ${detail}`);
  }
  return res.json();
}
