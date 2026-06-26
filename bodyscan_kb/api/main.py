"""
main.py — API FastAPI para BodyScan KB: Recomendação por IA Generativa.

Implementa M4: API de recomendação com todos os gates de governança clínica.

Contratos (seção 9 do PRD):
  POST /v1/recomendacoes  — orquestra gate → recuperação → regras → LLM
  POST /v1/ingestao/documento — ingere documento e gera embeddings
  GET  /v1/conhecimento/buscar — busca interna de chunks
  POST /v1/feedback — registra feedback de recomendação

Gates de governança (seção 8 do PRD):
  1. Gate de escalonamento (human-in-the-loop)
  2. Gate de conteúdo servível (vw_chunk_servivel)
  3. Sem números individuais (proibição explícita no prompt)
  4. Grounding + citação obrigatórios
  5. Auditoria (log_recomendacao)
  6. Recusa quando KB não cobre o tema (RF-12)
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

os.environ.setdefault("EMBED_PROVIDER", "local")

from api.models import (
    FeedbackRequest,
    FeedbackResponse,
    IngestaoRequest,
    IngestaoResponse,
    RecomendacaoRequest,
    RecomendacaoResponse,
    RespostaEscalonamento,
)
from api.services import (
    gerar_recomendacao_llm,
    registrar_feedback,
    registrar_log,
)
from ingestion.pipeline import (
    avaliar_gatilhos,
    conectar,
    ingerir_documento,
    recomendacoes_por_contexto,
    recuperar,
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://bodyscan:bodyscan_secret@localhost:5432/bodyscan_kb",
)

# Pool global gerenciado pelo lifespan
_pool = None


async def get_app_pool():
    """Retorna o pool da aplicação."""
    global _pool
    if _pool is None:
        _pool = await conectar(DATABASE_URL)
    return _pool


# -------------------------------------------------------------------------
# Lifespan (substitui on_event deprecated)
# -------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia ciclo de vida da aplicação."""
    global _pool
    _pool = await conectar(DATABASE_URL)
    print("[startup] Pool de conexões inicializado.")
    yield
    if _pool:
        await _pool.close()
        _pool = None
        print("[shutdown] Pool de conexões fechado.")


# -------------------------------------------------------------------------
# Aplicação FastAPI
# -------------------------------------------------------------------------
app = FastAPI(
    title="BodyScan KB — API de Recomendação",
    description=(
        "API de recomendação por IA Generativa com governança clínica. "
        "Baseada em RAG (Retrieval-Augmented Generation) com gates de segurança. "
        "ATENÇÃO: Nenhuma saída deve ser exposta a usuários finais sem sign-off clínico."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------------
# Health check
# -------------------------------------------------------------------------
@app.get("/health")
async def health_check():
    """Verifica saúde da API e conectividade com o banco."""
    try:
        pool = await get_app_pool()
        async with pool.acquire() as con:
            await con.fetchval("SELECT 1")
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": str(e)},
        )


# -------------------------------------------------------------------------
# POST /v1/recomendacoes — Endpoint principal (RF-06, RF-07, RF-08, RF-09, RF-12)
# -------------------------------------------------------------------------
@app.post(
    "/v1/recomendacoes",
    response_model=RecomendacaoResponse | RespostaEscalonamento,
    summary="Gera recomendação ancorada em RAG com governança clínica",
    description=(
        "Orquestra: gate de escalonamento → recuperação híbrida → "
        "camada de regras → geração LLM com grounding e citação. "
        "Proibido: prescrever fármacos, doses ou metas calóricas individuais. "
        "Recusa quando a KB não cobre o tema."
    ),
)
async def post_recomendacoes(req: RecomendacaoRequest):
    """
    Pipeline de recomendação com todos os gates de governança clínica.

    Seção 8 do PRD:
    1. Gate de escalonamento → bloqueia se detectar sinal de risco.
    2. Gate de conteúdo servível → exclui chunks com supervisão em fluxo autônomo.
    3. Sem números individuais → proibição explícita no prompt da LLM.
    4. Grounding + citação → LLM responde apenas com base nos chunks.
    5. Auditoria → log_recomendacao registra cada resposta.
    6. Recusa → sem chunks relevantes, recusa sem inventar.
    """
    pool = await get_app_pool()

    # ----------------------------------------------------------------
    # 1. Gate de escalonamento (human-in-the-loop) — RF-07
    # ----------------------------------------------------------------
    gate = await avaliar_gatilhos(pool, req.pergunta)
    if gate.bloqueado:
        # Registra log de escalonamento (auditoria RF-09)
        await registrar_log(
            pool,
            perfil_pseudonimo=req.pseudonimo,
            recomendacao_id=None,
            chunks_ids=[],
            modelo="gate_escalonamento",
            prompt_hash=hashlib.sha256(req.pergunta.encode()).hexdigest()[:16],
            houve_escalonamento=True,
            tipo_alerta=gate.tipo_alerta,
        )
        return RespostaEscalonamento(
            escalonar=True,
            tipo_alerta=gate.tipo_alerta,
            acao=gate.acao,
            mensagem=(
                "Sua mensagem contém um sinal que requer atenção profissional. "
                "Por favor, consulte um profissional de saúde habilitado."
            ),
        )

    # ----------------------------------------------------------------
    # 2. Recuperação híbrida com gate de conteúdo servível — RF-04, RF-08
    # ----------------------------------------------------------------
    metricas_dict = {m.biomarcador: m.valor for m in (req.metricas or [])}
    contextos = [req.contexto_clinico] if req.contexto_clinico else None

    chunks = await recuperar(
        pool,
        req.pergunta,
        contextos=contextos,
        incluir_supervisao=False,  # Gate: nunca servir conteúdo com supervisão em fluxo autônomo
        k=6,
    )

    # ----------------------------------------------------------------
    # 3. RF-12: Recusa explícita quando KB não cobre o tema
    # ----------------------------------------------------------------
    if not chunks:
        log_id = await registrar_log(
            pool,
            perfil_pseudonimo=req.pseudonimo,
            recomendacao_id=None,
            chunks_ids=[],
            modelo="sem_cobertura",
            prompt_hash=hashlib.sha256(req.pergunta.encode()).hexdigest()[:16],
            houve_escalonamento=False,
            tipo_alerta=None,
        )
        return RecomendacaoResponse(
            escalonar=False,
            recomendacoes=[],
            chunks=[],
            fontes=[],
            resposta_llm=(
                "Não encontrei informações na base de conhecimento que cubram "
                "este tema. Por favor, consulte um profissional de saúde habilitado "
                "para orientações específicas."
            ),
            log_id=str(log_id) if log_id else None,
            aviso="Tema não coberto pela base de conhecimento.",
        )

    # ----------------------------------------------------------------
    # 4. Camada de regras: recomendações elegíveis — RF-05
    # ----------------------------------------------------------------
    recs_elegiveis = []
    if req.contexto_clinico:
        recs_elegiveis = await recomendacoes_por_contexto(
            pool, req.contexto_clinico, metricas_dict
        )

    # ----------------------------------------------------------------
    # 5. Geração LLM com grounding e citação — RF-06
    # ----------------------------------------------------------------
    chunks_data = [
        {
            "id": c.id,
            "texto": c.texto,
            "dominio_slug": c.dominio_slug,
            "contexto_slugs": c.contexto_slugs,
            "nivel_evidencia": c.nivel_evidencia,
        }
        for c in chunks
    ]

    recs_data = [
        {
            "slug": r.slug,
            "titulo": r.titulo,
            "forca": r.forca,
        }
        for r in recs_elegiveis
    ]

    resposta_llm = await gerar_recomendacao_llm(
        pergunta=req.pergunta,
        chunks=chunks_data,
        recomendacoes=recs_data,
        contexto_clinico=req.contexto_clinico,
    )

    # ----------------------------------------------------------------
    # 6. Auditoria: registra log — RF-09
    # ----------------------------------------------------------------
    modelo_usado = os.getenv("LLM_MODEL", "gpt-4o-mini")
    prompt_hash = hashlib.sha256(
        (req.pergunta + json.dumps(chunks_data)).encode()
    ).hexdigest()[:16]

    log_id = await registrar_log(
        pool,
        perfil_pseudonimo=req.pseudonimo,
        recomendacao_id=None,
        chunks_ids=[c.id for c in chunks],
        modelo=modelo_usado,
        prompt_hash=prompt_hash,
        houve_escalonamento=False,
        tipo_alerta=None,
    )

    # Coleta fontes únicas dos chunks
    fontes = list({c.dominio_slug for c in chunks if c.dominio_slug})

    return RecomendacaoResponse(
        escalonar=False,
        recomendacoes=[
            {"slug": r.slug, "titulo": r.titulo, "forca": r.forca}
            for r in recs_elegiveis
        ],
        chunks=chunks_data,
        fontes=fontes,
        resposta_llm=resposta_llm,
        log_id=str(log_id) if log_id else None,
    )


# -------------------------------------------------------------------------
# POST /v1/ingestao/documento — Ingestão de documento (M2)
# -------------------------------------------------------------------------
@app.post(
    "/v1/ingestao/documento",
    response_model=IngestaoResponse,
    summary="Ingere documento e gera embeddings",
)
async def post_ingestao_documento(req: IngestaoRequest):
    """Ingere um documento da KB, gera chunks e embeddings."""
    pool = await get_app_pool()
    try:
        n_chunks = await ingerir_documento(pool, req.documento_id)
        return IngestaoResponse(
            documento_id=req.documento_id,
            chunks_gerados=n_chunks,
            status="ok",
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na ingestão: {e}")


# -------------------------------------------------------------------------
# GET /v1/conhecimento/buscar — Busca interna de chunks (RF-04)
# -------------------------------------------------------------------------
@app.get(
    "/v1/conhecimento/buscar",
    summary="Busca chunks na base de conhecimento (uso interno)",
)
async def get_conhecimento_buscar(
    q: str,
    contextos: str | None = None,
    k: int = 6,
):
    """Busca vetorial interna de chunks. Uso interno/debug."""
    pool = await get_app_pool()
    contextos_list = contextos.split(",") if contextos else None
    chunks = await recuperar(pool, q, contextos=contextos_list, k=k)
    return {
        "query": q,
        "chunks": [
            {
                "id": c.id,
                "texto": c.texto[:200] + "..." if len(c.texto) > 200 else c.texto,
                "distancia": c.distancia,
                "dominio_slug": c.dominio_slug,
                "contexto_slugs": c.contexto_slugs,
                "nivel_evidencia": c.nivel_evidencia,
            }
            for c in chunks
        ],
    }


# -------------------------------------------------------------------------
# POST /v1/feedback — Feedback de recomendação (RF-10)
# -------------------------------------------------------------------------
@app.post(
    "/v1/feedback",
    response_model=FeedbackResponse,
    summary="Registra feedback sobre uma recomendação emitida",
)
async def post_feedback(req: FeedbackRequest):
    """Registra feedback vinculado ao log de recomendação."""
    pool = await get_app_pool()
    try:
        await registrar_feedback(pool, req.log_id, req.util, req.comentario)
        return FeedbackResponse(ok=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao registrar feedback: {e}")
