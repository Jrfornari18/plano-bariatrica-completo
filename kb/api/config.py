"""
config.py — Configuração centralizada via variáveis de ambiente.
Usa pydantic-settings para validação e carregamento do .env.
"""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Banco de dados
    database_url: str = Field(
        default="postgresql://postgres@localhost/bodyscan_kb",
        description="DSN do PostgreSQL",
    )

    # OpenAI
    openai_api_key: str = Field(default="", description="Chave OpenAI")
    openai_api_base: str = Field(
        default="https://api.openai.com/v1",
        description="Base URL da API OpenAI (sobrescrita no sandbox)",
    )
    openai_embed_model: str = Field(
        default="text-embedding-3-small",
        description="Modelo de embedding OpenAI",
    )
    openai_chat_model: str = Field(
        default="gpt-4o-mini",
        description="Modelo de chat OpenAI",
    )

    # Dimensão do embedding — DEVE bater com schema.sql vector(N)
    embed_dim: int = Field(default=1536, description="Dimensão do vetor de embedding")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_env: str = Field(default="development")


@lru_cache
def get_settings() -> Settings:
    """Retorna instância singleton das configurações."""
    return Settings()
