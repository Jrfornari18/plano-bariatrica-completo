"""
Serviço de Embeddings — T3.
Abstração EmbeddingProvider com implementações plugáveis:
  - MockProvider: retorna vetores aleatórios (testes/dev)
  - SentenceTransformersProvider: local, sem API key
  - OpenAIProvider: via API (chave por variável de ambiente)

A troca de provider não quebra o schema — embedding_model_version
é persistido para permitir reindexação controlada (RNF-5).
"""
import asyncio
import hashlib
import logging
import math
import random
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Protocol

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Interface ─────────────────────────────────────────────────────────────────
class EmbeddingProvider(ABC):
    """Interface base para providers de embedding."""

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Identificador versionado do modelo (persiste no banco)."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensão do vetor de saída."""
        ...

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Gera embedding para um único texto."""
        ...

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Gera embeddings para múltiplos textos (padrão: sequencial)."""
        return [await self.embed(t) for t in texts]

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        """Similaridade cosseno entre dois vetores."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# ── Mock Provider (testes e desenvolvimento) ──────────────────────────────────
class MockEmbeddingProvider(EmbeddingProvider):
    """
    Provider determinístico baseado em hash do texto.
    Não requer dependências externas — ideal para testes e CI.
    """

    def __init__(self, dimension: int = 384):
        self._dimension = dimension
        self._version = f"mock-{dimension}d-v1"

    @property
    def model_version(self) -> str:
        return self._version

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(self, text: str) -> list[float]:
        # Seed determinístico baseado no hash do texto
        seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)
        vec = [rng.gauss(0, 1) for _ in range(self._dimension)]
        # Normalizar para vetor unitário
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm > 0 else vec


# ── Sentence Transformers Provider (local) ────────────────────────────────────
class SentenceTransformersProvider(EmbeddingProvider):
    """
    Provider local usando sentence-transformers.
    Não requer API key — adequado para MVP e ambientes sem GPU.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self._model_name = model_name
        self._model = None  # Lazy loading

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Carregando modelo SentenceTransformers: {self._model_name}")
                self._model = SentenceTransformer(self._model_name)
                logger.info("Modelo carregado com sucesso.")
            except ImportError:
                raise RuntimeError(
                    "sentence-transformers não instalado. "
                    "Execute: pip install sentence-transformers"
                )

    @property
    def model_version(self) -> str:
        return f"st-{self._model_name}-v1"

    @property
    def dimension(self) -> int:
        self._load_model()
        return self._model.get_sentence_embedding_dimension()

    async def embed(self, text: str) -> list[float]:
        self._load_model()
        result = await asyncio.to_thread(
            self._model.encode, text, normalize_embeddings=True
        )
        return result.tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self._load_model()
        results = await asyncio.to_thread(
            self._model.encode, texts, normalize_embeddings=True, batch_size=32
        )
        return [r.tolist() for r in results]


# ── OpenAI Provider ───────────────────────────────────────────────────────────
class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    Provider via API OpenAI.
    Chave lida exclusivamente de variável de ambiente (OPENAI_API_KEY).
    """

    def __init__(self, model: str = "text-embedding-3-small", dimension: int = 1536):
        self._model = model
        self._dimension = dimension
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                api_key = settings.openai_api_key
                if not api_key:
                    raise RuntimeError(
                        "OPENAI_API_KEY não configurado. "
                        "Defina a variável de ambiente antes de usar o provider OpenAI."
                    )
                self._client = AsyncOpenAI(
                    api_key=api_key,
                    base_url=settings.openai_api_base,
                )
            except ImportError:
                raise RuntimeError(
                    "openai não instalado. Execute: pip install openai"
                )
        return self._client

    @property
    def model_version(self) -> str:
        return f"openai-{self._model}-v1"

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(self, text: str) -> list[float]:
        client = self._get_client()
        response = await client.embeddings.create(
            model=self._model,
            input=text,
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        client = self._get_client()
        response = await client.embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]


# ── Factory ───────────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    """
    Retorna o provider configurado via EMBEDDING_PROVIDER.
    Singleton — carregado uma vez por processo.
    """
    provider = settings.embedding_provider.lower()
    logger.info(f"Inicializando EmbeddingProvider: {provider}")

    if provider == "mock":
        return MockEmbeddingProvider(dimension=settings.embedding_dimension)
    elif provider == "sentence_transformers":
        return SentenceTransformersProvider(model_name=settings.st_model_name)
    elif provider == "openai":
        return OpenAIEmbeddingProvider(
            model=settings.embedding_model,
            dimension=settings.embedding_dimension,
        )
    else:
        logger.warning(
            f"Provider '{provider}' desconhecido. Usando MockEmbeddingProvider."
        )
        return MockEmbeddingProvider(dimension=settings.embedding_dimension)
