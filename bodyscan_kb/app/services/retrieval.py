"""
Serviço de Recuperação RAG — T4, RF-A5, RF-E1, RF-E2.
Combina:
  1. Busca vetorial filtrada por domínio (top-k por similaridade cosseno)
  2. Expansão por grafo de concept_relation cross-domínio
  3. Aplicação de vínculos validados como restrições/prioridades
"""
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.l1_knowledge import Concept, ConceptRelation, KnowledgeChunk
from app.services.embedding import EmbeddingProvider, get_embedding_provider

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Resultado de busca ────────────────────────────────────────────────────────
class ChunkResult:
    def __init__(
        self,
        chunk_id: str,
        source_id: str,
        dominio: str,
        conteudo: str,
        score: float,
        metadata: dict[str, Any] | None = None,
    ):
        self.chunk_id = chunk_id
        self.source_id = source_id
        self.dominio = dominio
        self.conteudo = conteudo
        self.score = score
        self.metadata = metadata or {}


# ── Serviço de Recuperação ────────────────────────────────────────────────────
class RetrievalService:
    """
    Serviço de recuperação RAG com suporte a:
    - busca vetorial filtrada por domínio
    - expansão por grafo de conceitos cross-domínio
    - aplicação de vínculos validados
    """

    def __init__(self, provider: EmbeddingProvider | None = None):
        self._provider = provider or get_embedding_provider()

    async def search(
        self,
        db: AsyncSession,
        query: str,
        dominio: str | None = None,
        top_k: int = 5,
        similarity_threshold: float = 0.0,
    ) -> list[ChunkResult]:
        """
        Busca vetorial nos chunks de conhecimento.
        Filtra por domínio quando especificado.
        Retorna top-k ordenados por similaridade cosseno.
        """
        # Gerar embedding da query
        query_embedding = await self._provider.embed(query)

        # Buscar todos os chunks com embedding (filtrado por domínio)
        stmt = select(KnowledgeChunk).where(
            KnowledgeChunk.embedding.is_not(None)
        )
        if dominio:
            stmt = stmt.where(KnowledgeChunk.dominio == dominio)

        result = await db.execute(stmt)
        chunks = result.scalars().all()

        if not chunks:
            logger.debug(f"Nenhum chunk encontrado para domínio={dominio}")
            return []

        # Calcular similaridade cosseno para cada chunk
        scored: list[tuple[float, KnowledgeChunk]] = []
        for chunk in chunks:
            if chunk.embedding:
                score = self._provider.cosine_similarity(
                    query_embedding, chunk.embedding
                )
                if score >= similarity_threshold:
                    scored.append((score, chunk))

        # Ordenar por score decrescente e retornar top-k
        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]

        return [
            ChunkResult(
                chunk_id=c.id,
                source_id=c.source_id,
                dominio=c.dominio,
                conteudo=c.conteudo,
                score=round(score, 4),
                metadata=c.metadata_ or {},
            )
            for score, c in top
        ]

    async def expand_cross_domain(
        self,
        db: AsyncSession,
        concept_ids: list[str],
        max_hops: int = 1,
    ) -> list[dict[str, Any]]:
        """
        Expande conceitos via arestas cross-domínio no grafo.
        Retorna relações onde dominio_origem ≠ dominio_destino.
        """
        if not concept_ids:
            return []

        relations = []
        visited = set(concept_ids)

        current_ids = list(concept_ids)
        for _ in range(max_hops):
            if not current_ids:
                break

            stmt = select(ConceptRelation).where(
                ConceptRelation.concept_origem_id.in_(current_ids),
                ConceptRelation.dominio_origem != ConceptRelation.dominio_destino,
            )
            result = await db.execute(stmt)
            found = result.scalars().all()

            next_ids = []
            for rel in found:
                relations.append({
                    "relation_id": rel.id,
                    "origem_id": rel.concept_origem_id,
                    "destino_id": rel.concept_destino_id,
                    "dominio_origem": rel.dominio_origem,
                    "dominio_destino": rel.dominio_destino,
                    "tipo_relacao": rel.tipo_relacao,
                    "forca": rel.forca,
                })
                if rel.concept_destino_id not in visited:
                    visited.add(rel.concept_destino_id)
                    next_ids.append(rel.concept_destino_id)

            current_ids = next_ids

        return relations

    async def find_concepts_by_text(
        self,
        db: AsyncSession,
        text: str,
        dominio: str | None = None,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Busca conceitos por similaridade semântica (via embedding do concept).
        """
        query_embedding = await self._provider.embed(text)

        stmt = select(Concept).where(Concept.embedding.is_not(None))
        if dominio:
            stmt = stmt.where(Concept.dominio == dominio)

        result = await db.execute(stmt)
        concepts = result.scalars().all()

        scored = []
        for c in concepts:
            if c.embedding:
                score = self._provider.cosine_similarity(query_embedding, c.embedding)
                scored.append((score, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "concept_id": c.id,
                "dominio": c.dominio,
                "nome": c.nome,
                "nome_canonico": c.nome_canonico,
                "score": round(score, 4),
            }
            for score, c in scored[:top_k]
        ]


def get_retrieval_service() -> RetrievalService:
    """Dependency injection do FastAPI."""
    return RetrievalService()
