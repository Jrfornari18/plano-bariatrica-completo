"""
Serviço de Orquestração do Assistente — T9, RF-E1, RF-E2.
Combina:
  1. Snapshot fisiológico mais recente do usuário
  2. Memórias semânticas ativas (busca por similaridade)
  3. Busca vetorial RAG nos três domínios
  4. Expansão cross-domínio via grafo de conceitos
  5. Aplicação de vínculos validados como restrições/prioridades
  6. Registro em recuperacao_log (RF-E3, T10)
"""
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.l3_subject import PerfilFisiologicoSnapshot
from app.models.l5_retrieval import RecuperacaoLog
from app.schemas.user_memory_schemas import (
    RetrieveContextItem,
    RetrieveRequest,
    RetrieveResponse,
)
from app.services.memory import MemoryService, get_memory_service
from app.services.retrieval import RetrievalService, get_retrieval_service

logger = logging.getLogger(__name__)


class AssistantService:
    """
    Orquestrador de recuperação para o assistente BodyScan.
    Monta o contexto completo a partir de todas as camadas de memória e conhecimento.
    """

    def __init__(
        self,
        retrieval: RetrievalService | None = None,
        memory: MemoryService | None = None,
    ):
        self._retrieval = retrieval or get_retrieval_service()
        self._memory = memory or get_memory_service()

    async def retrieve(
        self,
        db: AsyncSession,
        usuario_id: str,
        request: RetrieveRequest,
    ) -> RetrieveResponse:
        """
        Recuperação orquestrada completa (RF-E1).
        Retorna contexto montado + log_id para feedback posterior.
        """
        dominios = request.dominios or ["fisiologia", "treino", "nutricao"]
        contexto: list[RetrieveContextItem] = []
        chunks_log: list[dict] = []
        memorias_log: list[dict] = []

        # 1. Snapshot fisiológico mais recente
        snapshot = await self._get_snapshot_recente(db, usuario_id)

        # 2. Memórias semânticas similares à query
        memorias_aplicadas: list[dict[str, Any]] = []
        if request.incluir_memoria:
            semanticas = await self._memory.buscar_semantica_similar(
                db, usuario_id, request.query, top_k=5
            )
            for score, mem in semanticas:
                contexto.append(RetrieveContextItem(
                    tipo="memoria_semantica",
                    dominio=mem.dominio,
                    conteudo=mem.afirmacao,
                    score=round(score, 4),
                    id=mem.id,
                ))
                memorias_aplicadas.append({
                    "memoria_id": mem.id,
                    "tipo": mem.tipo,
                    "dominio": mem.dominio,
                    "confianca": mem.confianca,
                })
                memorias_log.append({"memoria_id": mem.id, "tipo": mem.tipo, "dominio": mem.dominio})

        # 3. Busca vetorial RAG por domínio
        for dominio in dominios:
            chunks = await self._retrieval.search(
                db,
                query=request.query,
                dominio=dominio,
                top_k=request.top_k,
            )
            for chunk in chunks:
                contexto.append(RetrieveContextItem(
                    tipo="chunk",
                    dominio=chunk.dominio,
                    conteudo=chunk.conteudo,
                    score=chunk.score,
                    id=chunk.chunk_id,
                ))
                chunks_log.append({
                    "chunk_id": chunk.chunk_id,
                    "score": chunk.score,
                    "dominio": chunk.dominio,
                })

        # 4. Expansão cross-domínio via grafo de conceitos
        vinculos_validados: list[dict[str, Any]] = []
        if request.incluir_cross_dominio:
            # Buscar conceitos relacionados à query
            conceitos = await self._retrieval.find_concepts_by_text(
                db, request.query, top_k=3
            )
            concept_ids = [c["concept_id"] for c in conceitos]

            if concept_ids:
                relacoes = await self._retrieval.expand_cross_domain(
                    db, concept_ids, max_hops=1
                )
                for rel in relacoes:
                    contexto.append(RetrieveContextItem(
                        tipo="relacao_cross",
                        dominio=f"{rel['dominio_origem']}→{rel['dominio_destino']}",
                        conteudo=(
                            f"Relação '{rel['tipo_relacao']}' "
                            f"(força={rel.get('forca', '?')})"
                        ),
                        score=rel.get("forca"),
                        id=rel["relation_id"],
                    ))

            # 5. Aplicar vínculos validados como restrições (RF-E2)
            vinculos = await self._memory.listar_vinculos_validados(db, usuario_id)
            for v in vinculos:
                vinculos_validados.append({
                    "vinculo_id": v.id,
                    "tipo_vinculo": v.tipo_vinculo,
                    "descricao": v.descricao,
                    "forca": v.forca,
                })
                contexto.append(RetrieveContextItem(
                    tipo="vinculo_cross",
                    dominio="transversal",
                    conteudo=v.descricao or f"Vínculo {v.tipo_vinculo}",
                    score=v.forca,
                    id=v.id,
                ))

        # 6. Registrar log de recuperação (RF-E3)
        log = RecuperacaoLog(
            usuario_id=usuario_id,
            query=request.query,
            dominios_consultados=dominios,
            chunks_recuperados=chunks_log,
            memorias_aplicadas=memorias_log,
            resposta_gerada=f"Contexto montado: {len(contexto)} itens",
        )
        db.add(log)
        await db.flush()

        # Ordenar contexto por score decrescente
        contexto.sort(
            key=lambda x: x.score if x.score is not None else 0.0,
            reverse=True,
        )

        return RetrieveResponse(
            query=request.query,
            snapshot_recente=self._snapshot_to_response(snapshot),
            contexto=contexto,
            memorias_aplicadas=memorias_aplicadas,
            vinculos_validados=vinculos_validados,
            log_id=log.id,
        )

    async def _get_snapshot_recente(
        self,
        db: AsyncSession,
        usuario_id: str,
    ) -> PerfilFisiologicoSnapshot | None:
        """Retorna o snapshot fisiológico mais recente do usuário."""
        stmt = (
            select(PerfilFisiologicoSnapshot)
            .where(PerfilFisiologicoSnapshot.usuario_id == usuario_id)
            .order_by(PerfilFisiologicoSnapshot.data_medicao.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    def _snapshot_to_response(self, snapshot):
        """Converte snapshot ORM para schema de resposta."""
        if snapshot is None:
            return None
        from app.schemas.user_memory_schemas import SnapshotResponse
        return SnapshotResponse.model_validate(snapshot)

    async def registrar_feedback(
        self,
        db: AsyncSession,
        log_id: str,
        feedback: str,
    ) -> bool:
        """Registra feedback do usuário em um log de recuperação."""
        stmt = select(RecuperacaoLog).where(RecuperacaoLog.id == log_id)
        result = await db.execute(stmt)
        log = result.scalar_one_or_none()
        if not log:
            return False
        log.feedback = feedback
        await db.flush()
        return True


def get_assistant_service() -> AssistantService:
    """Dependency injection do FastAPI."""
    return AssistantService()
