"""
Aplicação FastAPI principal — BodyScan Motor de Recomendação.
F0: healthcheck, CORS, rate limiting, logging estruturado.
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db.session import check_db_connection
from app.api.v1 import recommendations, profiles, exercises

setup_logging()
logger = get_logger(__name__)

# ─── Rate limiter ─────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização e encerramento da aplicação."""
    logger.info("Iniciando BodyScan Recommendation API...")

    # Verificar conexão com banco
    db_ok = await check_db_connection()
    if not db_ok:
        logger.error("FALHA: Banco de dados não acessível em '%s'", settings.database_path)
    else:
        logger.info("Banco de dados OK: %s", settings.database_path)

    # Carregar índice FAISS se disponível
    try:
        from app.services.embedding_service import load_or_create_index
        loaded = load_or_create_index()
        if loaded:
            logger.info("Índice FAISS carregado com sucesso")
        else:
            logger.warning("Índice FAISS não encontrado — execute scripts/ingest_embeddings.py")
    except Exception as exc:
        logger.warning("Falha ao carregar índice FAISS: %s", exc)

    yield
    logger.info("BodyScan Recommendation API encerrada")


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="BodyScan — Motor de Recomendação de Treinos",
    description="API RAG híbrida: filtro SQL + busca semântica + geração LLM",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (RNF — restrito à origem do frontend em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ─── Middleware de request_id ─────────────────────────────────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    from app.core.logging import new_request_id
    rid = new_request_id()
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


# ─── Healthcheck (F0) ────────────────────────────────────────────────────────
@app.get("/health", tags=["infra"])
async def health():
    """F0: Healthcheck — verifica banco e índice vetorial."""
    db_ok = await check_db_connection()

    from app.services.embedding_service import _faiss_index
    vector_ok = _faiss_index is not None

    return {
        "status": "ok" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
        "vector_index": "loaded" if vector_ok else "not_loaded",
        "version": "1.0.0",
    }


# ─── Routers ─────────────────────────────────────────────────────────────────
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(profiles.router, prefix="/api/v1")
app.include_router(exercises.router, prefix="/api/v1")
