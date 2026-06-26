"""
Configuração central da aplicação via variáveis de ambiente.
Nenhum segredo deve ser inserido diretamente neste arquivo.
"""
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Aplicação ─────────────────────────────────────────────────────────────
    app_name: str = "BodyScan KB & Memory"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # ── Banco de dados ─────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./bodyscan_kb.db"
    # Para produção: postgresql+asyncpg://user:pass@host:5432/db

    # ── Embeddings ─────────────────────────────────────────────────────────────
    embedding_provider: Literal["openai", "sentence_transformers", "mock"] = "mock"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    embedding_model_version: str = "v1"

    # Sentence Transformers (local, sem API key)
    st_model_name: str = "all-MiniLM-L6-v2"

    # OpenAI (apenas via variável de ambiente — nunca hardcoded)
    openai_api_key: str = ""
    openai_api_base: str = "https://api.openai.com/v1"

    # ── RAG ────────────────────────────────────────────────────────────────────
    rag_top_k: int = 5
    rag_similarity_threshold: float = 0.70

    # ── Sessão / memória ───────────────────────────────────────────────────────
    session_ttl_minutes: int = 60

    # ── CORS ───────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
