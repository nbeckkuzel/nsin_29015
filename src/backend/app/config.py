"""Konfiguracja z zmiennych środowiskowych (.env)."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    vision_model: str = os.getenv("VISION_MODEL", "gpt-4o")
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4o")

    def require_key(self) -> None:
        if not self.openai_api_key:
            raise RuntimeError(
                "Brak OPENAI_API_KEY. Skopiuj .env.example do .env i wpisz klucz."
            )


settings = Settings()
