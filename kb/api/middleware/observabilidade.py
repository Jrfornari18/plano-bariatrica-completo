"""
observabilidade.py — Middleware de observabilidade e logging estruturado.

RNF-04: Logs estruturados com rastreio de request_id, latência e modelo.
RNF-05: Métricas de latência e taxa de escalonamento disponíveis.
LGPD: Sem PII nos logs — apenas pseudônimo e IDs.
"""
from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("bodyscan.kb.access")


class ObservabilidadeMiddleware(BaseHTTPMiddleware):
    """
    Middleware que:
    - Gera request_id único por requisição
    - Registra latência, status e endpoint em log estruturado
    - Injeta request_id no header de resposta para rastreio
    - Não loga corpos de requisição (proteção LGPD)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start = time.perf_counter()

        # Injeta request_id no estado da requisição
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception as exc:
            elapsed = (time.perf_counter() - start) * 1000
            logger.error(
                "request_id=%s method=%s path=%s status=500 latency_ms=%.1f error=%s",
                request_id,
                request.method,
                request.url.path,
                elapsed,
                str(exc),
            )
            raise

        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "request_id=%s method=%s path=%s status=%d latency_ms=%.1f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            elapsed,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Latency-Ms"] = f"{elapsed:.1f}"
        return response
