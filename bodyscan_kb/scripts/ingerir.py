#!/usr/bin/env python3
"""
ingerir.py — Script CLI para ingestão de documentos no BodyScan KB.

Uso:
    python scripts/ingerir.py                    # ingere todos os documentos pendentes
    python scripts/ingerir.py --doc <uuid>       # ingere documento específico
    python scripts/ingerir.py --verificar        # verifica chunks sem embedding
"""

import argparse
import asyncio
import os
import sys

# Adiciona o diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from ingestion.pipeline import (
    conectar,
    ingerir_documento,
    ingerir_todos_documentos,
)


async def verificar_chunks(pool) -> None:
    """Verifica e reporta chunks sem embedding."""
    import asyncpg

    async with pool.acquire() as con:
        total = await con.fetchval("SELECT COUNT(*) FROM chunk_conhecimento")
        sem_embedding = await con.fetchval(
            "SELECT COUNT(*) FROM chunk_conhecimento WHERE embedding IS NULL"
        )
        servivel = await con.fetchval(
            "SELECT COUNT(*) FROM vw_chunk_servivel"
        )
        docs = await con.fetch(
            "SELECT id::text, titulo FROM documento_conhecimento ORDER BY titulo"
        )

    print(f"\n=== Status dos Chunks ===")
    print(f"Total de chunks:          {total}")
    print(f"Chunks sem embedding:     {sem_embedding}")
    print(f"Chunks serviveis (view):  {servivel}")
    print(f"\nDocumentos ({len(docs)}):")
    for d in docs:
        print(f"  {d['id']} — {d['titulo']}")


async def main() -> None:
    parser = argparse.ArgumentParser(description="BodyScan KB — Ingestão de documentos")
    parser.add_argument("--doc", help="UUID do documento a ingerir")
    parser.add_argument("--verificar", action="store_true", help="Verificar status dos chunks")
    args = parser.parse_args()

    dsn = os.getenv(
        "DATABASE_URL",
        "postgresql://bodyscan:bodyscan_secret@localhost:5432/bodyscan_kb",
    )

    print(f"Conectando ao banco: {dsn.split('@')[1] if '@' in dsn else dsn}")
    pool = await conectar(dsn)

    try:
        if args.verificar:
            await verificar_chunks(pool)
            return

        if args.doc:
            print(f"Ingerindo documento: {args.doc}")
            n = await ingerir_documento(pool, args.doc)
            print(f"✓ {n} chunks gerados para o documento {args.doc}")
        else:
            print("Ingerindo todos os documentos pendentes...")
            resultados = await ingerir_todos_documentos(pool)
            total = sum(v for v in resultados.values() if v >= 0)
            erros = sum(1 for v in resultados.values() if v < 0)
            print(f"\n=== Resultado da Ingestão ===")
            for doc_id, n in resultados.items():
                status = f"✓ {n} chunks" if n >= 0 else "✗ ERRO"
                print(f"  {doc_id}: {status}")
            print(f"\nTotal: {total} chunks gerados, {erros} erros")

    finally:
        await pool.close()


if __name__ == "__main__":
    asyncio.run(main())
