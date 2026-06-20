"""FastAPI: import screenshotów, odczyt dashboardu, zamykanie, czat RAG."""
from __future__ import annotations

import uuid
from datetime import date

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import ai, rag, storage
from .config import settings
from .models import ChatRequest, ChatResponse, DashboardState, Task

app = FastAPI(title="Notes RAG Dashboard")

# Frontend (Vite) chodzi na innym porcie — pozwalamy mu się łączyć.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/tasks", response_model=DashboardState)
def get_tasks() -> DashboardState:
    return storage.get_state()


@app.post("/import", response_model=DashboardState)
async def import_screenshots(files: list[UploadFile] = File(...)) -> DashboardState:
    settings.require_key()
    new_tasks: list[Task] = []
    for f in files:
        image_bytes = await f.read()
        items = ai.read_note_from_image(image_bytes)  # Vision: lista niewykonanych zadań
        for parsed in items:
            cls = ai.classify(parsed)  # klasyfikacja + RAG dla każdego zadania
            task = Task(
                id=f"t_{uuid.uuid4().hex[:8]}",
                raw_text=parsed["raw_text"],
                source_image=f.filename,
                title=parsed["title"],
                label=parsed["label"],
                created_date=date.today(),  # data importu, nie z treści notatki
                status=cls["status"],
                ai_priority=cls["ai_priority"],
                ai_reasoning=cls["ai_reasoning"],
            )
            new_tasks.append(task)
            # zasil bazę wektorową — ten sam Chroma obsłuży potem czat
            rag.index_note(
                task.id, task.raw_text, task.label, task.status,
                task.created_date.isoformat(),
            )
    storage.add_tasks(new_tasks)
    return storage.get_state()


@app.patch("/tasks/{task_id}/close")
def close_task(task_id: str) -> dict:
    if not storage.close_task(task_id):
        raise HTTPException(404, "Task nie istnieje lub już zamknięty")
    return {"ok": True}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    settings.require_key()
    answer, sources = ai.answer_query(req.message)
    return ChatResponse(answer=answer, sources=sources)
