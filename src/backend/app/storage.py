"""Storage na pliku JSON. Stan tasków + log burndown.

Świadoma decyzja: age_days i przejście do 'stale' liczymy dynamicznie
przy każdym odczycie (z created_date względem dzisiaj), zamiast trzymać
na stałe w pliku. Dzięki temu task starzeje się sam, bez przepisywania JSON.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from threading import Lock

from .models import BurndownPoint, DashboardState, Task

DATA_FILE = Path(__file__).parent.parent / "data" / "tasks.json"
STALE_THRESHOLD_DAYS = 14  # po tylu dniach task wpada do kolumny 'stale'

_lock = Lock()


def _empty_state() -> dict:
    return {"tasks": [], "burndown": [], "labels": []}


def _read_raw() -> dict:
    if not DATA_FILE.exists():
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps(_empty_state(), indent=2, ensure_ascii=False))
        return _empty_state()
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _write_raw(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )


def _enrich(task_dict: dict) -> Task:
    """Dolicz age_days i ewentualnie podbij status do 'stale'."""
    created = task_dict["created_date"]
    if isinstance(created, str):
        created = date.fromisoformat(created)
    age = (date.today() - created).days
    task_dict = {**task_dict, "age_days": max(age, 0)}

    # Wiek to osobna oś od ai_priority: stary task = 'stale' niezależnie
    # od tego, co AI pierwotnie przypisało. To pożądane — taki jest najgroźniejszy.
    if task_dict["alive"] and age >= STALE_THRESHOLD_DAYS:
        task_dict["status"] = "stale"
    return Task(**task_dict)


def get_state() -> DashboardState:
    with _lock:
        raw = _read_raw()
    tasks = [_enrich(t) for t in raw["tasks"] if t.get("alive", True)]
    burndown = [BurndownPoint(**b) for b in raw["burndown"]]
    return DashboardState(tasks=tasks, burndown=burndown, labels=raw["labels"])


def add_tasks(new_tasks: list[Task]) -> None:
    with _lock:
        raw = _read_raw()
        existing_labels = set(raw["labels"])
        for t in new_tasks:
            raw["tasks"].append(t.model_dump(mode="json"))
            existing_labels.add(t.label)
        raw["labels"] = sorted(existing_labels)
        _write_raw(raw)


def close_task(task_id: str) -> bool:
    """Oznacz task jako zamknięty i dopisz wpis do burndown logu."""
    with _lock:
        raw = _read_raw()
        found = False
        for t in raw["tasks"]:
            if t["id"] == task_id and t.get("alive", True):
                t["alive"] = False
                t["closed_at"] = datetime.now().isoformat()
                found = True
                break
        if not found:
            return False

        remaining = sum(1 for t in raw["tasks"] if t.get("alive", True))
        today = date.today().isoformat()
        # zaktualizuj dzisiejszy wpis albo dodaj nowy
        for point in raw["burndown"]:
            if point["date"] == today:
                point["remaining"] = remaining
                point["closed_today"] += 1
                break
        else:
            raw["burndown"].append(
                {"date": today, "remaining": remaining, "closed_today": 1}
            )
        _write_raw(raw)
        return True
