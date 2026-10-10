"""Configuração central do backend VesteIA.

Lê variáveis de ambiente (opcionalmente de backend/.env). Nenhum valor secreto é
registrado em log nem devolvido pela API.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "sim", "on"}


def _int(name: str, default: int, low: int = 0, high: int = 1_000_000) -> int:
    try:
        value = int(os.getenv(name, str(default)).strip())
    except ValueError:
        return default
    return max(low, min(high, value))


@dataclass(frozen=True)
class Settings:
    # Banco legado (catálogo, perfis, provador 2D antigo). Desligado por padrão.
    database_enabled: bool = field(default_factory=lambda: _bool("DATABASE_ENABLED", False))
    cors_origins: tuple[str, ...] = field(default_factory=lambda: tuple(
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()))

    # Provedores. Os nomes TRYON_* foram mantidos da versão 1.5.8.
    avatar_provider: str = field(default_factory=lambda: os.getenv("AVATAR_PROVIDER", "photo").strip().lower())
    tryon_provider: str = field(default_factory=lambda: os.getenv("TRYON_PROVIDER", "mock").strip().lower())
    tryon_enabled: bool = field(default_factory=lambda: _bool("TRYON_ENABLED", False))
    # Chamadas com custo exigem esta confirmação explícita, além da chave.
    paid_enabled: bool = field(default_factory=lambda: _bool("AI_PAID_ENABLED", False))

    # OpenAI Images API (somente backend).
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-2").strip())
    openai_quality: str = field(default_factory=lambda: os.getenv("OPENAI_IMAGE_QUALITY", "medium").strip().lower())
    openai_size: str = field(default_factory=lambda: os.getenv("OPENAI_IMAGE_SIZE", "1024x1536").strip())
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip().rstrip("/"))
    openai_timeout: int = field(default_factory=lambda: _int("OPENAI_TIMEOUT_SECONDS", 240, 30, 900))

    # Limites persistentes (SQLite em backend/data). 0 bloqueia o tipo de chamada.
    daily_limit_paid: int = field(default_factory=lambda: _int("AI_DAILY_LIMIT_PAID", 20))
    total_limit_paid: int = field(default_factory=lambda: _int("AI_TOTAL_LIMIT_PAID", 100))
    daily_limit_local: int = field(default_factory=lambda: _int("AI_DAILY_LIMIT_LOCAL", 200))
    session_limit: int = field(default_factory=lambda: _int("AI_SESSION_LIMIT", 12))
    sessions_per_ip_daily: int = field(default_factory=lambda: _int("AI_SESSIONS_PER_IP_DAILY", 30, 1))
    max_sizes_per_request: int = field(default_factory=lambda: _int("AI_MAX_SIZES_PER_REQUEST", 4, 1, 8))
    max_garments: int = field(default_factory=lambda: _int("AI_MAX_GARMENTS", 4, 1, 6))
    max_concurrent: int = field(default_factory=lambda: _int("AI_MAX_CONCURRENT", 1, 1, 8))
    usage_db_path: Path = field(default_factory=lambda: Path(os.getenv("AI_USAGE_DB", str(BACKEND_DIR / "data" / "usage.sqlite3"))))

    # Sessão e upload.
    session_ttl_minutes: int = field(default_factory=lambda: _int("STUDIO_SESSION_TTL_MINUTES", 60, 5, 24 * 60))
    access_code: str = field(default_factory=lambda: os.getenv("STUDIO_ACCESS_CODE", "").strip())
    max_upload_mb: int = field(default_factory=lambda: _int("MAX_UPLOAD_MB", 8, 1, 20))

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024


def get_settings() -> Settings:
    # Recriado a cada chamada: barato e permite testes com variáveis diferentes.
    return Settings()
