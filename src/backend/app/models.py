"""Modele danych — kontrakt między backendem a frontendem."""
from __future__ import annotations

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel

Status = Literal["urgent", "progress", "stale"]
Priority = Literal["high", "medium", "low"]


class Task(BaseModel):
    id: str
    raw_text: str
    source_image: Optional[str] = None
    title: str
    label: str
    created_date: date
    # status (kolumna) i ai_priority (osobna oś) celowo rozdzielone
    status: Status
    ai_priority: Priority
    ai_reasoning: str = ""
    alive: bool = True
    closed_at: Optional[str] = None

    # age_days liczone dynamicznie przy odczycie — patrz storage.enrich()
    age_days: int = 0


class BurndownPoint(BaseModel):
    date: str
    remaining: int
    closed_today: int


class DashboardState(BaseModel):
    tasks: list[Task]
    burndown: list[BurndownPoint]
    labels: list[str]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []  # id notatek użytych jako kontekst
