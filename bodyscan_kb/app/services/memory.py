"""
Serviço de Memória — T7, T8, RF-D1 a RF-D4.
Gerencia memória episódica, semântica, vínculos cross-domínio e contexto de sessão.
Guardrail: vínculos cross-domínio nunca são marcados como 'validado' automaticamente.
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.l4_memory import (
    ContextoSessao,
    MemoriaEpisodica,
    MemoriaSemantica,
    MemoriaVinculoCrossDominio,
)
from app.schemas.user_memory_schemas import (
    EpisodioCreate,
    SemanticaCreate,
    VinculoCrossCreate,
)
from app.services.embedding import get_embedding_provider

logger = logging.getLogger(__name__)
settings = get_settings()


class MemoryService:
    """Serviço unificado de memória por usuário."""

    def __init__(self):
        self._embedding_provider = get_embedding_provider()

    # ── Memória Episódica ─────────────────────────────────────────────────────
    async def registrar_episodio(
        self,
        db: AsyncSession,
        usuario_id: str,
        data: EpisodioCreate,
    ) -> MemoriaEpisodica:
        """Registra um evento na linha do tempo do usuário."""
        episodio = MemoriaEpisodica(
            usuario_id=usuario_id,
            tipo_evento=data.tipo_evento,
            dominio=data.dominio,
            ref_entidade_tipo=data.ref_entidade_tipo,
            ref_entidade_id=data.ref_entidade_id,
            payload=data.payload or {},
            ocorrido_em=data.ocorrido_em or datetime.now(timezone.utc),
        )
        db.add(episodio)
        await db.flush()
        logger.debug(
            f"Episódio registrado: usuario={usuario_id} tipo={data.tipo_evento}"
        )
        return episodio

    async def listar_episodios(
        self,
        db: AsyncSession,
        usuario_id: str,
        dominio: str | None = None,
        limit: int = 50,
    ) -> list[MemoriaEpisodica]:
        """Lista episódios do usuário, opcionalmente filtrado por domínio."""
        stmt = (
            select(MemoriaEpisodica)
            .where(MemoriaEpisodica.usuario_id == usuario_id)
            .order_by(MemoriaEpisodica.ocorrido_em.desc())
            .limit(limit)
        )
        if dominio:
            stmt = stmt.where(MemoriaEpisodica.dominio == dominio)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ── Memória Semântica ─────────────────────────────────────────────────────
    async def registrar_semantica(
        self,
        db: AsyncSession,
        usuario_id: str,
        data: SemanticaCreate,
    ) -> MemoriaSemantica:
        """Registra um fato/preferência de longo prazo sobre o usuário."""
        # Gerar embedding da afirmação para recuperação semântica futura
        embedding = await self._embedding_provider.embed(data.afirmacao)

        semantica = MemoriaSemantica(
            usuario_id=usuario_id,
            dominio=data.dominio,
            tipo=data.tipo,
            afirmacao=data.afirmacao,
            confianca=data.confianca,
            evidencia_episodios=data.evidencia_episodios or [],
            valido_de=data.valido_de,
            valido_ate=data.valido_ate,
            ativo=data.ativo,
            embedding=embedding,
        )
        db.add(semantica)
        await db.flush()
        logger.debug(
            f"Memória semântica registrada: usuario={usuario_id} tipo={data.tipo}"
        )
        return semantica

    async def listar_semantica_ativa(
        self,
        db: AsyncSession,
        usuario_id: str,
        dominio: str | None = None,
    ) -> list[MemoriaSemantica]:
        """Lista memórias semânticas ativas e válidas temporalmente."""
        agora = datetime.now(timezone.utc)
        stmt = (
            select(MemoriaSemantica)
            .where(
                MemoriaSemantica.usuario_id == usuario_id,
                MemoriaSemantica.ativo == True,
            )
            .order_by(MemoriaSemantica.confianca.desc())
        )
        if dominio:
            stmt = stmt.where(MemoriaSemantica.dominio == dominio)
        result = await db.execute(stmt)
        memorias = result.scalars().all()

        # Filtrar por validade temporal
        return [
            m for m in memorias
            if (m.valido_ate is None or m.valido_ate > agora)
            and (m.valido_de is None or m.valido_de <= agora)
        ]

    async def buscar_semantica_similar(
        self,
        db: AsyncSession,
        usuario_id: str,
        query: str,
        top_k: int = 5,
    ) -> list[tuple[float, MemoriaSemantica]]:
        """Busca memórias semânticas por similaridade com a query."""
        from app.services.embedding import EmbeddingProvider
        provider = self._embedding_provider
        query_embedding = await provider.embed(query)

        memorias = await self.listar_semantica_ativa(db, usuario_id)
        scored = []
        for m in memorias:
            if m.embedding:
                score = provider.cosine_similarity(query_embedding, m.embedding)
                scored.append((score, m))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]

    # ── Vínculos Cross-Domínio ────────────────────────────────────────────────
    async def registrar_vinculo(
        self,
        db: AsyncSession,
        usuario_id: str,
        data: VinculoCrossCreate,
    ) -> MemoriaVinculoCrossDominio:
        """
        Registra um vínculo cross-domínio.
        GUARDRAIL: status sempre inicia em 'hipotese' — nunca 'validado' automaticamente.
        """
        # Validar que pelo menos 2 domínios estão preenchidos (RF-D3)
        dominios_preenchidos = sum([
            data.conceito_fisiologia_id is not None,
            data.conceito_treino_id is not None,
            data.conceito_nutricao_id is not None,
        ])
        if dominios_preenchidos < 2:
            raise ValueError(
                "Um vínculo cross-domínio exige pelo menos 2 domínios preenchidos."
            )

        vinculo = MemoriaVinculoCrossDominio(
            usuario_id=usuario_id,
            conceito_fisiologia_id=data.conceito_fisiologia_id,
            conceito_treino_id=data.conceito_treino_id,
            conceito_nutricao_id=data.conceito_nutricao_id,
            tipo_vinculo=data.tipo_vinculo,
            descricao=data.descricao,
            forca=data.forca,
            gerado_por=data.gerado_por,
            evidencia=data.evidencia or {},
            status="hipotese",  # GUARDRAIL: sempre hipotese
        )
        db.add(vinculo)
        await db.flush()
        logger.debug(
            f"Vínculo cross-domínio registrado como hipotese: usuario={usuario_id}"
        )
        return vinculo

    async def listar_vinculos_validados(
        self,
        db: AsyncSession,
        usuario_id: str,
    ) -> list[MemoriaVinculoCrossDominio]:
        """Lista apenas vínculos com status='validado' (revisados por humano)."""
        stmt = select(MemoriaVinculoCrossDominio).where(
            MemoriaVinculoCrossDominio.usuario_id == usuario_id,
            MemoriaVinculoCrossDominio.status == "validado",
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def listar_vinculos(
        self,
        db: AsyncSession,
        usuario_id: str,
        status: str | None = None,
    ) -> list[MemoriaVinculoCrossDominio]:
        """Lista vínculos, opcionalmente filtrado por status."""
        stmt = select(MemoriaVinculoCrossDominio).where(
            MemoriaVinculoCrossDominio.usuario_id == usuario_id
        )
        if status:
            stmt = stmt.where(MemoriaVinculoCrossDominio.status == status)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ── Contexto de Sessão ────────────────────────────────────────────────────
    async def criar_ou_atualizar_sessao(
        self,
        db: AsyncSession,
        usuario_id: str,
        sessao_id: str,
        janela_contexto: dict,
        objetivo_sessao: str | None = None,
    ) -> ContextoSessao:
        """Cria ou atualiza o contexto de trabalho da sessão atual."""
        from datetime import timedelta

        expira_em = datetime.now(timezone.utc) + timedelta(
            minutes=settings.session_ttl_minutes
        )

        # Verificar se já existe sessão ativa
        stmt = select(ContextoSessao).where(
            ContextoSessao.usuario_id == usuario_id,
            ContextoSessao.sessao_id == sessao_id,
        )
        result = await db.execute(stmt)
        sessao = result.scalar_one_or_none()

        if sessao:
            sessao.janela_contexto = janela_contexto
            sessao.objetivo_sessao = objetivo_sessao
            sessao.expira_em = expira_em
        else:
            sessao = ContextoSessao(
                usuario_id=usuario_id,
                sessao_id=sessao_id,
                janela_contexto=janela_contexto,
                objetivo_sessao=objetivo_sessao,
                expira_em=expira_em,
            )
            db.add(sessao)

        await db.flush()
        return sessao


def get_memory_service() -> MemoryService:
    """Dependency injection do FastAPI."""
    return MemoryService()
