import type { Task } from "../types";

// Kolor i pasek wieku — im starszy task, tym groźniejszy sygnał.
function ageColor(age: number): string {
  if (age >= 14) return "var(--red)";
  if (age >= 7) return "var(--orange)";
  return "var(--amber)";
}

function ageBars(age: number): string {
  const filled = age >= 14 ? 5 : age >= 7 ? 3 : 1;
  return "█".repeat(filled) + "░".repeat(5 - filled);
}

function formatDate(iso: string): string {
  const [, m, d] = iso.split("-");
  return `${d}.${m}`;
}

interface Props {
  task: Task;
  onClose: (id: string) => void;
}

export function TaskCard({ task, onClose }: Props) {
  const color = ageColor(task.age_days);
  return (
    <div className="task" style={{ borderLeft: `3px solid ${color}` }}>
      <button
        className="task-close"
        aria-label="Zamknij task"
        onClick={() => onClose(task.id)}
      >
        ×
      </button>
      <p className="task-title">{task.title}</p>
      <div className="task-meta">
        <span className="task-label">{task.label}</span>
        <span className="task-age" style={{ color }} title={task.ai_reasoning}>
          {ageBars(task.age_days)} {task.age_days}d
        </span>
        <span className="task-priority">{task.ai_priority}</span>
        <span className="task-date">{formatDate(task.created_date)}</span>
      </div>
    </div>
  );
}
