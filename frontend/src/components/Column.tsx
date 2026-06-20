import type { Status, Task } from "../types";
import { TaskCard } from "./TaskCard";

const META: Record<Status, { label: string; cls: string }> = {
  urgent: { label: "URGENT", cls: "col-urgent" },
  progress: { label: "IN PROGRESS", cls: "col-progress" },
  stale: { label: "STALE", cls: "col-stale" },
};

interface Props {
  status: Status;
  tasks: Task[];
  onClose: (id: string) => void;
}

export function Column({ status, tasks, onClose }: Props) {
  const meta = META[status];
  return (
    <div className="column">
      <div className={`column-head ${meta.cls}`}>
        <span>▰</span>
        <span>{meta.label}</span>
        <span className="count">{String(tasks.length).padStart(2, "0")}</span>
      </div>
      {tasks.length === 0 ? (
        <div className="col-empty">· · ·</div>
      ) : (
        tasks.map((t) => <TaskCard key={t.id} task={t} onClose={onClose} />)
      )}
    </div>
  );
}
