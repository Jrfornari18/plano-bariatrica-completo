"""
embed_provider.py — Provedor de embeddings plugável para BodyScan KB.

Estratégia:
  1. Se EMBED_PROVIDER=openai e a API de embeddings estiver disponível → OpenAI.
  2. Fallback: sentence-transformers (all-MiniLM-L6-v2, 384 dims) com projeção
     linear para EMBED_DIM=1536 via padding determinístico.
  3. Para produção, configure EMBED_PROVIDER=openai e OPENAI_API_KEY real.

A dimensão DEVE bater com EMBED_DIM em schema.sql (NOTA 1).
"""

from __future__ import annotations

import os
from typing import Sequence

# Dimensão do embedding — DEVE bater com schema.sql (NOTA 1).
EMBED_DIM: int = int(os.getenv("EMBED_DIM", "1536"))
EMBED_MODEL: str = os.getenv("EMBED_MODEL", "text-embedding-3-small")
EMBED_PROVIDER: str = os.getenv("EMBED_PROVIDER", "local")

# Cache do modelo local
_local_model = None


def _get_local_model():
    """Carrega o modelo sentence-transformers (lazy loading)."""
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        model_name = os.getenv("LOCAL_EMBED_MODEL", "all-MiniLM-L6-v2")
        print(f"[embed] Carregando modelo local: {model_name}")
        _local_model = SentenceTransformer(model_name)
    return _local_model


def _pad_to_dim(vetor: list[float], dim: int) -> list[float]:
    """Projeta/padeia um vetor para a dimensão alvo de forma determinística.

    Se o vetor for menor, repete ciclicamente com fator de escala decrescente.
    Se for maior, trunca.
    """
    n = len(vetor)
    if n == dim:
        return vetor
    if n > dim:
        return vetor[:dim]
    # Padding cíclico com escala decrescente para manter unicidade
    resultado = list(vetor)
    ciclo = 0
    while len(resultado) < dim:
        escala = 0.5 ** (ciclo + 1)
        faltam = dim - len(resultado)
        resultado.extend([v * escala for v in vetor[:faltam]])
        ciclo += 1
    return resultado[:dim]


async def embed_local(textos: Sequence[str]) -> list[list[float]]:
    """Gera embeddings locais com sentence-transformers.

    Usa all-MiniLM-L6-v2 (384 dims) e projeta para EMBED_DIM via padding.
    Para produção, substitua por um modelo de 1536 dims ou use OpenAI.
    """
    model = _get_local_model()
    embeddings = model.encode(list(textos), convert_to_numpy=True)
    return [_pad_to_dim(emb.tolist(), EMBED_DIM) for emb in embeddings]


async def embed_openai(textos: Sequence[str]) -> list[list[float]]:
    """Gera embeddings via OpenAI API (async).

    Usa text-embedding-3-small por padrão (1536 dims).
    """
    import openai
    client = openai.AsyncOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
    )
    response = await client.embeddings.create(
        model=EMBED_MODEL,
        input=list(textos),
    )
    return [item.embedding for item in response.data]


async def embed_fn(textos: Sequence[str]) -> list[list[float]]:
    """Função de embedding principal — seleciona provedor via EMBED_PROVIDER.

    EMBED_PROVIDER=openai → OpenAI API (produção)
    EMBED_PROVIDER=local  → sentence-transformers (desenvolvimento/fallback)
    """
    provider = EMBED_PROVIDER.lower()
    if provider == "openai":
        try:
            return await embed_openai(textos)
        except Exception as e:
            print(f"[embed] OpenAI falhou ({e}), usando fallback local")
            return await embed_local(textos)
    else:
        return await embed_local(textos)
