"""
Configurações da aplicação via variáveis de ambiente (RNF-02).
Nenhum segredo deve ser hardcoded aqui.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Banco de dados
    database_path: str = "app/db/knowledge_base.db"

    # Embeddings
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    vector_backend: str = "faiss"  # faiss | sqlite-vec
    vector_index_path: str = "app/db/faiss_index.bin"
    vector_ids_path: str = "app/db/faiss_ids.json"
    top_k_default: int = 8

    # LLM
    llm_provider: str = "openai_compatible"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_timeout_seconds: int = 20

    # API
    cors_origins: str = "*"
    rate_limit_per_minute: int = 30
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
