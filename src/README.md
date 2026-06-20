# Notes RAG Dashboard

Aplikacja, która przyjmuje screenshoty notatek z Apple Notes, klasyfikuje je
przez AI (OpenAI Vision + klasyfikacja z kontekstem RAG) i buduje dashboard
zadań w estetyce cassette futurism. Taski zamyka się krzyżykiem; wykres
burndown śledzi tempo zamykania. Okno czatu odpytuje notatki przez RAG
("co mam jeszcze otwartego z konferencji X?").

## Architektura

- **Frontend**: React + Vite + TypeScript (katalog `frontend/`)
- **Backend**: FastAPI (katalog `backend/`)
- **AI**: OpenAI Vision (odczyt obrazu) + chat completions (klasyfikacja, czat)
- **RAG**: ChromaDB — jedna baza wektorowa, zasilana przy imporcie,
  odpytywana przy klasyfikacji i w czacie
- **Storage**: plik JSON (`backend/data/tasks.json`)

## Uruchomienie — backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # wpisz swój OPENAI_API_KEY
uvicorn app.main:app --reload
```

API wstanie na http://localhost:8000 (dokumentacja: /docs).

## Endpointy

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET    | `/tasks` | stan dashboardu (taski + burndown + etykiety) |
| POST   | `/import` | batch upload screenshotów → klasyfikacja |
| PATCH  | `/tasks/{id}/close` | zamknij task, dopisz do burndown |
| POST   | `/chat` | pytanie RAG do notatek |

## Model danych

Status (`urgent`/`progress`/`stale`) i `ai_priority` (`high`/`medium`/`low`)
to dwie osobne osie: status decyduje o kolumnie, priorytet o wadze. Wiek
(`age_days`) liczony jest dynamicznie; po 14 dniach task wpada do `stale`
niezależnie od priorytetu — bo taki task jest najgroźniejszy.
