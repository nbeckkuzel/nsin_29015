import { useState } from "react";
import { sendChat } from "../api";

interface Msg {
  role: "user" | "bot";
  text: string;
  sources?: string[];
}

export function ChatPanel() {
  const [log, setLog] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    const q = input.trim();
    if (!q || busy) return;
    setInput("");
    setLog((l) => [...l, { role: "user", text: q }]);
    setBusy(true);
    try {
      const res = await sendChat(q);
      setLog((l) => [...l, { role: "bot", text: res.answer, sources: res.sources }]);
    } catch (e) {
      setLog((l) => [
        ...l,
        { role: "bot", text: `Błąd połączenia z API. Sprawdź, czy backend działa. (${String(e)})` },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="panel">
      <div className="panel-head">
        <span>◇ QUERY // RAG</span>
        <span className="legend">{busy ? "...thinking" : "ready"}</span>
      </div>
      <div className="chat-log">
        {log.length === 0 ? (
          <div className="chat-empty">
            Zapytaj o notatki, np. „co mam jeszcze z Carpathian Startup Fest?"
          </div>
        ) : (
          log.map((m, i) => (
            <div key={i}>
              <div className={`chat-msg ${m.role === "user" ? "chat-user" : "chat-bot"}`}>
                {m.text}
              </div>
              {m.sources && m.sources.length > 0 && (
                <div className="chat-sources">źródła: {m.sources.join(", ")}</div>
              )}
            </div>
          ))
        )}
      </div>
      <div className="chat-input-row">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="zapytaj dashboard..."
          disabled={busy}
        />
        <button className="btn" onClick={submit} disabled={busy}>
          SEND
        </button>
      </div>
    </div>
  );
}
