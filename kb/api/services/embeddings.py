"""
embeddings.py — Serviço de embeddings plugável.

Estratégia de fallback:
  1. Tenta OpenAI text-embedding-3-small (EMBED_DIM=1536) via API.
  2. Se a API não suportar /embeddings (sandbox), usa sentence-transformers
     all-MiniLM-L6-v2 (EMBED_DIM=384) localmente.

Em produção, configure OPENAI_API_KEY e EMBED_PROVIDER=openai.
No sandbox de desenvolvimento, EMBED_PROVIDER=local é usado automaticamente.
"""
from __future__ import annotations

import os
import logging
from typing import Sequence

from ..config import get_settings

logger = logging.getLogger(__name__)

# Provedor: 'openai' | 'local'
_EMBED_PROVIDER = os.environ.get("EMBED_PROVIDER", "auto")

# Cache do modelo local
_local_model = None


def _get_local_model():
    """Carrega o modelo sentence-transformers na primeira chamada."""
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Carregando modelo local all-MiniLM-L6-v2 (dim=384)...")
        _local_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _local_model


async def embed_openai(textos: Sequence[str]) -> list[list[float]]:
    """Gera embeddings via OpenAI API."""
    from openai import AsyncOpenAI

    settings = get_settings()
    base_url = os.environ.get("OPENAI_API_BASE", settings.openai_api_base)
    client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=base_url)

    response = await client.embeddings.create(
        model=settings.openai_embed_model,
        input=list(textos),
    )
    return [item.embedding for item in response.data]


async def embed_local(textos: Sequence[str]) -> list[list[float]]:
    """Gera embeddings localmente via sentence-transformers (dim=384)."""
    import asyncio
    model = _get_local_model()
    loop = asyncio.get_event_loop()
    # Executa em thread para não bloquear o event loop
    vetores = await loop.run_in_executor(
        None, lambda: model.encode(list(textos), convert_to_numpy=True).tolist()
    )
    return vetores


async def embed(textos: Sequence[str]) -> list[list[float]]:
    """
    Gera embeddings para uma lista de textos.

    Seleciona o provedor baseado em EMBED_PROVIDER:
    - 'openai': usa OpenAI API (produção)
    - 'local': usa sentence-transformers (desenvolvimento)
    - 'auto': tenta OpenAI, cai para local em caso de erro
    """
    settings = get_settings()
    provider = _EMBED_PROVIDER

    if provider == "openai":
        vetores = await embed_openai(textos)
    elif provider == "local":
        vetores = await embed_local(textos)
    else:  # auto
        try:
            vetores = await embed_openai(textos)
            logger.debug("Usando OpenAI para embeddings")
        except Exception as exc:
            logger.warning(
                "OpenAI embeddings indisponível (%s), usando modelo local", exc
            )
            vetores = await embed_local(textos)

    # Valida dimensão contra configuração
    for v in vetores:
        if len(v) != settings.embed_dim:
            raise ValueError(
                f"Dimensão do embedding ({len(v)}) != EMBED_DIM ({settings.embed_dim}). "
                "Ajuste EMBED_DIM no .env e o vector(N) no schema.sql."
            )
    return vetores
