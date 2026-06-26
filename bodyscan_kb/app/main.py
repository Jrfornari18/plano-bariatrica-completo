"""
Ponto de entrada da aplicação BodyScan KB & Memory.
T1 — App sobe; GET /health retorna 200; nenhum segredo em código.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import create_all_tables
from app.core.logging import setup_logging

# Routers (importados após criação)
from app.api.kb_router import router as kb_router
from app.api.users_router import router as users_router
from app.api.memory_router import router as memory_router
from app.api.assistant_router import router as assistant_router

settings = get_settings()
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização e encerramento da aplicação."""
    # Cria tabelas no banco (MVP — em produção usar Alembic)
    await create_all_tables()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Módulo de Base de Conhecimento (RAG) e Memória personalizada "
        "para o assistente BodyScan — Fisiologia, Treino e Nutrição."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(kb_router, prefix="/kb", tags=["Knowledge Base"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(memory_router, prefix="/memory", tags=["Memory"])
app.include_router(assistant_router, prefix="/assistant", tags=["Assistant"])


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """Verifica se a aplicação está operacional."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }
