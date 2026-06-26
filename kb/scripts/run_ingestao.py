"""
run_ingestao.py — Script de linha de comando para ingestão de embeddings.

Uso:
    cd kb/
    python scripts/run_ingestao.py
    python scripts/run_ingestao.py --doc-id <uuid>
"""
from __future__ import annotations

import asyncio
import argparse
import logging
import sys
import os

# Garante que o pacote api seja encontrado
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from api.database import get_pool, close_pool
from api.services.ingestao import ingerir_documento, ingerir_todos_documentos

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("run_ingestao")


async def main(doc_id: str | None = None) -> None:
    pool = await get_pool()
    try:
        if doc_id:
            logger.info("Ingerindo documento específico: %s", doc_id)
            n = await ingerir_documento(pool, doc_id)
            logger.info("Concluído: %d chunks gerados para %s", n, doc_id)
        else:
            logger.info("Ingerindo todos os documentos sem embedding...")
            resultados = await ingerir_todos_documentos(pool)
            total = sum(v for v in resultados.values() if v > 0)
            erros = sum(1 for v in resultados.values() if v < 0)
            logger.info(
                "Ingestão concluída: %d documentos, %d chunks totais, %d erros",
                len(resultados),
                total,
                erros,
            )
            for doc, n in resultados.items():
                status = f"{n} chunks" if n >= 0 else "ERRO"
                logger.info("  %s -> %s", doc, status)
    finally:
        await close_pool()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BodyScan KB — Ingestão de embeddings")
    parser.add_argument("--doc-id", help="UUID do documento a ingerir (opcional)")
    args = parser.parse_args()
    asyncio.run(main(args.doc_id))
