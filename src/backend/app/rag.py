"""Warstwa RAG. Jedna baza wektorowa, dwa zastosowania:

1. import -> retrieve_context_for(): pobiera podobne wcześniejsze notatki,
   żeby klasyfikacja nowej była spójna z historią.
2. chat  -> retrieve_for_query(): pobiera notatki pasujące do pytania
   użytkownika ("co mam jeszcze z konferencji X?").

ChromaDB trzyma embeddingi treści notatek + metadane (label, status, data).
"""
from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

from .config import settings

CHROMA_DIR = Path(__file__).parent.parent / "data" / "chroma"

_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
_embed_fn = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.openai_api_key,
    model_name="text-embedding-3-small",
)
_collection = _client.get_or_create_collection(
    name="notes", embedding_function=_embed_fn
)


def index_note(task_id: str, text: str, label: str, status: str, created_date: str) -> None:
    """Dodaj notatkę do bazy wektorowej (wołane przy imporcie)."""
    _collection.upsert(
        ids=[task_id],
        documents=[text],
        metadatas=[{"label": label, "status": status, "created_date": created_date}],
    )


def retrieve_context_for(text: str, k: int = 3) -> list[str]:
    """Podobne wcześniejsze notatki — kontekst dla klasyfikacji nowej."""
    if _collection.count() == 0:
        return []
    res = _collection.query(query_texts=[text], n_results=min(k, _collection.count()))
    return res["documents"][0] if res["documents"] else []


def retrieve_for_query(query: str, k: int = 5) -> tuple[list[str], list[str]]:
    """Notatki pasujące do pytania w czacie. Zwraca (teksty, id źródeł)."""
    if _collection.count() == 0:
        return [], []
    res = _collection.query(query_texts=[query], n_results=min(k, _collection.count()))
    docs = res["documents"][0] if res["documents"] else []
    ids = res["ids"][0] if res["ids"] else []
    return docs, ids
