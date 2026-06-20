import { useEffect, useMemo, useRef, useState } from "react";
import { closeTask, fetchTasks, importScreenshots } from "./api";
import { Burndown } from "./components/Burndown";
import { ChatPanel } from "./components/ChatPanel";
import { Column } from "./components/Column";
import type { DashboardState, Status } from "./types";

const STATUSES: Status[] = ["urgent", "progress", "stale"];

export default function App() {
  const [state, setState] = useState<DashboardState | null>(null);
  const [filter, setFilter] = useState<string>("all");
  const [error, setError] = useState<string | null>(null);
  const [importing, setImporting] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  async function load() {
    try {
      setState(await fetchTasks());
      setError(null);
    } catch (e) {
      setError(`Nie można połączyć z backendem (localhost:8000). Czy uvicorn działa? ${String(e)}`);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function onClose(id: string) {
    // optymistycznie usuń z widoku, potem potwierdź z serwerem
    setState((s) =>
      s ? { ...s, tasks: s.tasks.filter((t) => t.id !== id) } : s
    );
    try {
      await closeTask(id);
      await load(); // odśwież, żeby burndown się zaktualizował
    } catch (e) {
      setError(`Nie udało się zamknąć taska. ${String(e)}`);
      await load();
    }
  }

  async function onFiles(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    if (files.length === 0) return;
    setImporting(true);
    setError(null);
    try {
      const next = await importScreenshots(files);
      setState(next);
    } catch (err) {
      setError(`Import nie powiódł się. ${String(err)}`);
    } finally {
      setImporting(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  const filtered = useMemo(() => {
    if (!state) return [];
    return filter === "all"
      ? state.tasks
      : state.tasks.filter((t) => t.label === filter);
  }, [state, filter]);

  if (!state && !error) {
    return <div className="loading">◷ Ładowanie mission control...</div>;
  }

  const total = state?.tasks.length ?? 0;
  const today = new Date().toLocaleDateString("pl-PL", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
  });

  return (
    <div className="app">
      <div className="masthead">
        <div className="masthead-title">
          <span className="led" />
          <span>NOTE-CTRL // TASK MONITOR</span>
        </div>
        <span className="masthead-sys">
          SYS {today} · {total} ACTIVE
        </span>
      </div>

      {error && <div className="banner">⚠ {error}</div>}

      <div className="toolbar">
        <input
          ref={fileInput}
          type="file"
          accept="image/*"
          multiple
          onChange={onFiles}
          style={{ display: "none" }}
        />
        <button
          className={`btn ${importing ? "btn-busy" : ""}`}
          onClick={() => fileInput.current?.click()}
          disabled={importing}
        >
          {importing ? "◷ PRZETWARZAM..." : "▲ WRZUĆ SCREENSHOTY"}
        </button>

        <span style={{ width: 12 }} />

        <button
          className={`chip ${filter === "all" ? "on" : ""}`}
          onClick={() => setFilter("all")}
        >
          [ ALL ]
        </button>
        {state?.labels.map((lab) => (
          <button
            key={lab}
            className={`chip ${filter === lab ? "on" : ""}`}
            onClick={() => setFilter(lab)}
          >
            {lab.toUpperCase()}
          </button>
        ))}
      </div>

      <div className="board">
        {STATUSES.map((s) => (
          <Column
            key={s}
            status={s}
            tasks={filtered.filter((t) => t.status === s)}
            onClose={onClose}
          />
        ))}
      </div>

      <div className="lower">
        <Burndown data={state?.burndown ?? []} />
        <ChatPanel />
      </div>

      <div className="deco-strip" />
    </div>
  );
}
