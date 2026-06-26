"""
main.py — Aplicação FastAPI principal do BodyScan KB.

Endpoints (seção 9 do PRD):
  POST /v1/recomendacoes       — Recomendação com governança clínica
  POST /v1/ingestao/documento  — Ingestão de documento + embeddings
  GET  /v1/conhecimento/buscar — Busca híbrida (interno)
  POST /v1/feedback            — Feedback de recomendação
  GET  /health                 — Health check
"""
from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import get_pool, close_pool
from .routers import recomendacoes, ingestao, conhecimento, feedback, lgpd, metricas
from .middleware.observabilidade import ObservabilidadeMiddleware

# Logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="BodyScan KB — API de Recomendação",
    description=(
        "Base de conhecimento de fisiologia do emagrecimento com "
        "recomendação por IA Generativa e governança clínica. "
        "Conteúdo educativo — não substitui avaliação profissional."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — ajustar origens em produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.api_env == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Observabilidade: logging estruturado + request_id
app.add_middleware(ObservabilidadeMiddleware)

# Routers
app.include_router(recomendacoes.router)
app.include_router(ingestao.router)
app.include_router(conhecimento.router)
app.include_router(feedback.router)
app.include_router(lgpd.router)
app.include_router(metricas.router)


@app.on_event("startup")
async def startup():
    logger.info(
        "BodyScan KB iniciando: env=%s embed_dim=%d",
        settings.api_env,
        settings.embed_dim,
    )
    # Inicializa pool de conexão
    await get_pool()
    logger.info("Pool de banco de dados inicializado")


@app.on_event("shutdown")
async def shutdown():
    await close_pool()
    logger.info("Pool de banco de dados encerrado")


@app.get("/health", tags=["infra"])
async def health():
    """Health check — verifica conectividade com o banco."""
    try:
        pool = await get_pool()
        async with pool.acquire() as con:
            await con.fetchval("SELECT 1")
        return {"status": "ok", "db": "connected", "env": settings.api_env}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


@app.get("/", tags=["infra"])
async def root():
    return {
        "service": "BodyScan KB",
        "version": "1.0.0",
        "docs": "/docs",
        "aviso": (
            "Conteúdo educativo. Não substitui avaliação médica ou nutricional. "
            "Recomendações com peso clínico exigem supervisão profissional."
        ),
    }
