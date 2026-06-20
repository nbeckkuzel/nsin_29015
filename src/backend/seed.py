"""Zasiewa data/tasks.json przykładowymi taskami — bez wywołań OpenAI.

Uruchom z katalogu backend:  python seed.py
Pozwala zobaczyć dashboard i przetestować frontend, zanim podepniesz API.
"""
from __future__ import annotations

from datetime import date, timedelta

from app import storage
from app.models import Task

# wyczyść istniejący stan, żeby seed był powtarzalny
if storage.DATA_FILE.exists():
    storage.DATA_FILE.unlink()

today = date.today()


def days_ago(n: int) -> date:
    return today - timedelta(days=n)


SAMPLE = [
    Task(
        id="t_seed01",
        raw_text="Follow-up z funduszem VC — wysłać metryki do piątku",
        source_image="seed/img_01.png",
        title="Follow-up: inwestor z funduszu",
        label="Carpathian Startup Fest",
        created_date=days_ago(2),
        status="urgent",
        ai_priority="high",
        ai_reasoning="Deadline w treści + kontekst konferencji",
    ),
    Task(
        id="t_seed02",
        raw_text="Wysłać deck pitchowy do mentora po sesji",
        source_image="seed/img_02.png",
        title="Wysłać deck do mentora",
        label="Carpathian Startup Fest",
        created_date=days_ago(3),
        status="urgent",
        ai_priority="high",
        ai_reasoning="Oczekiwanie po stronie mentora",
    ),
    Task(
        id="t_seed03",
        raw_text="Odpowiedzieć na maila od klienta w sprawie wyceny",
        source_image="seed/img_03.png",
        title="Odpowiedź na maila od klienta",
        label="Personal",
        created_date=days_ago(1),
        status="urgent",
        ai_priority="medium",
        ai_reasoning="Klient czeka na odpowiedź",
    ),
    Task(
        id="t_seed04",
        raw_text="Przygotować drugą wersję pitcha na podstawie feedbacku",
        source_image="seed/img_04.png",
        title="Przygotować pitch v2",
        label="Carpathian Startup Fest",
        created_date=days_ago(5),
        status="progress",
        ai_priority="medium",
        ai_reasoning="Praca w toku, brak twardego deadline",
    ),
    Task(
        id="t_seed05",
        raw_text="Zsynchronizować backlog zespołu po standupie",
        source_image="seed/img_05.png",
        title="Zsynchronizować backlog",
        label="Daily standup",
        created_date=days_ago(4),
        status="progress",
        ai_priority="low",
        ai_reasoning="Rutynowe zadanie organizacyjne",
    ),
    Task(
        id="t_seed06",
        raw_text="Spisać action pointy z porannego standupu",
        source_image="seed/img_06.png",
        title="Spisać action pointy",
        label="Daily standup",
        created_date=days_ago(6),
        status="progress",
        ai_priority="low",
        ai_reasoning="Notatki do uzupełnienia",
    ),
    Task(
        id="t_seed07",
        raw_text="Zarejestrować domenę dla projektu startupowego",
        source_image="seed/img_07.png",
        title="Zarejestrować domenę",
        label="Personal",
        created_date=days_ago(18),
        status="progress",  # storage podbije do 'stale' (age >= 14)
        ai_priority="medium",
        ai_reasoning="Wisi długo, blokuje launch strony",
    ),
    Task(
        id="t_seed08",
        raw_text="Dograć kawę networkingową z poznanym founderem",
        source_image="seed/img_08.png",
        title="Networking: dograć kawę",
        label="Carpathian Startup Fest",
        created_date=days_ago(21),
        status="progress",  # storage podbije do 'stale'
        ai_priority="low",
        ai_reasoning="Kontakt stygnie im dłużej zwlekasz",
    ),
]

storage.add_tasks(SAMPLE)
state = storage.get_state()

print(f"Zasiano {len(state.tasks)} tasków.")
print("Rozkład po kolumnach:")
for col in ("urgent", "progress", "stale"):
    items = [t for t in state.tasks if t.status == col]
    print(f"  {col:9} {len(items)}")
print("Etykiety:", ", ".join(state.labels))
print("\nGotowe. Odśwież GET /tasks w /docs albo zacznij frontend.")