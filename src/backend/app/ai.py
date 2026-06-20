"""Wywołania OpenAI: odczyt obrazu (Vision), klasyfikacja, czat RAG."""
from __future__ import annotations

import base64
import json
from datetime import date

from openai import OpenAI

from .config import settings
from . import rag

_client = OpenAI(api_key=settings.openai_api_key)


def read_note_from_image(image_bytes: bytes) -> dict:
    """Vision: wyciągnij z screenshota notatki tytuł, treść, datę i etykietę.

    W tytułach notatek Apple są daty i etykiety (np. 'Carpathian Startup Fest').
    Prosimy model, żeby je sparsował.
    """
    b64 = base64.b64encode(image_bytes).decode()
    prompt = (
        "To zrzut ekranu notatki z aplikacji Apple Notes. "
        "Wyciągnij dane i zwróć WYŁĄCZNIE JSON (bez markdown) o polach: "
        "title (krótki tytuł zadania), raw_text (pełna treść notatki), "
        "label (etykieta/wydarzenie z tytułu, np. nazwa konferencji; jeśli brak: 'Personal'), "
        "created_date (data w formacie YYYY-MM-DD; jeśli brak, użyj dzisiejszej)."
    )
    resp = _client.chat.completions.create(
        model=settings.vision_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64}"},
                    },
                ],
            }
        ],
    )
    data = _parse_json(resp.choices[0].message.content)
    data.setdefault("created_date", date.today().isoformat())
    data.setdefault("label", "Personal")
    return data


def classify(note: dict) -> dict:
    """Klasyfikacja z kontekstem RAG: status + ai_priority + uzasadnienie.

    Status i ai_priority to OSOBNE osie:
    - status: urgent | progress | stale  (która kolumna)
    - ai_priority: high | medium | low   (jak ważne wg treści)
    """
    context = rag.retrieve_context_for(note["raw_text"], k=3)
    context_block = (
        "\n".join(f"- {c}" for c in context)
        if context
        else "(brak wcześniejszych podobnych notatek)"
    )
    prompt = (
        "Sklasyfikuj zadanie z notatki. Zwróć WYŁĄCZNIE JSON o polach: "
        "status (jedno z: urgent, progress, stale), "
        "ai_priority (jedno z: high, medium, low), "
        "ai_reasoning (jedno zdanie po polsku, dlaczego). "
        "status to kolumna na boardzie, ai_priority to waga zadania — to dwie różne osie.\n\n"
        f"Podobne wcześniejsze notatki (kontekst):\n{context_block}\n\n"
        f"Notatka do klasyfikacji:\n{note['raw_text']}"
    )
    resp = _client.chat.completions.create(
        model=settings.chat_model,
        messages=[{"role": "user", "content": prompt}],
    )
    out = _parse_json(resp.choices[0].message.content)
    out.setdefault("status", "progress")
    out.setdefault("ai_priority", "medium")
    out.setdefault("ai_reasoning", "")
    return out


def answer_query(message: str) -> tuple[str, list[str]]:
    """Czat RAG: odpowiedz na pytanie o dashboard z kontekstu notatek."""
    docs, ids = rag.retrieve_for_query(message, k=5)
    context_block = (
        "\n".join(f"- {d}" for d in docs) if docs else "(brak pasujących notatek)"
    )
    prompt = (
        "Jesteś asystentem dashboardu zadań. Odpowiedz zwięźle po polsku na pytanie "
        "użytkownika, opierając się WYŁĄCZNIE na poniższych notatkach. "
        "Jeśli nie ma odpowiedzi w notatkach, powiedz to wprost.\n\n"
        f"Notatki:\n{context_block}\n\nPytanie: {message}"
    )
    resp = _client.chat.completions.create(
        model=settings.chat_model,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip(), ids


def _parse_json(text: str) -> dict:
    """Wyłuskaj JSON nawet jeśli model owinął go w ```json ... ```."""
    cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)
