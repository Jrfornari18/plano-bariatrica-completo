"""
Log estruturado com request_id para rastreabilidade (RNF-05).
Sem dados sensíveis nos logs.
"""
import logging
import json
import sys
import uuid
from contextvars import ContextVar
from typing import Optional
from app.core.config import settings

request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        # Adiciona campos extras (ex.: etapa do RAG, tempo)
        for key in ("rag_step", "duration_ms", "candidates_count", "top_k_count"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def new_request_id() -> str:
    rid = str(uuid.uuid4())
    request_id_var.set(rid)
    return rid
