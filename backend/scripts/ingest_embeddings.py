"""
Script de ingestão de embeddings (RF-01).
Vetoriza a view vw_exercicios_documento e constrói o índice FAISS.
Execute uma vez antes de iniciar a API, ou a cada atualização da base.

Uso:
    cd backend
    python scripts/ingest_embeddings.py
"""
import sys
import os
import asyncio

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.db.session import get_db
from app.services.embedding_service import build_index, encode_text, search_similar

setup_logging()
logger = get_logger("ingest_embeddings")


async def fetch_documents():
    """Busca todos os documentos da view vw_exercicios_documento."""
    async with get_db() as conn:
        async with conn.execute(
            "SELECT exercicio_id, nome, documento FROM vw_exercicios_documento ORDER BY exercicio_id"
        ) as cursor:
            rows = await cursor.fetchall()
    return [(row["exercicio_id"], row["nome"], row["documento"]) for row in rows]


async def main():
    logger.info("=== Ingestão de Embeddings — BodyScan ===")
    logger.info("Modelo: %s", settings.embedding_model)
    logger.info("Backend vetorial: %s", settings.vector_backend)

    # Buscar documentos
    logger.info("Buscando documentos da view vw_exercicios_documento...")
    docs = await fetch_documents()
    logger.info("Encontrados %d documentos", len(docs))

    if not docs:
        logger.error("Nenhum documento encontrado. Verifique o banco de dados.")
        sys.exit(1)

    exercise_ids = [d[0] for d in docs]
    documents = [d[2] for d in docs]

    # Construir índice
    logger.info("Construindo índice vetorial...")
    build_index(exercise_ids, documents)
    logger.info("Índice construído com sucesso: %d vetores", len(exercise_ids))

    # Teste de validação (critério de aceite RF-01)
    logger.info("\n=== Teste de validação ===")
    test_queries = [
        ("queimar gordura sem equipamento", ["Burpee", "Mountain climber", "Polichinelo"]),
        ("força peitoral", ["Supino", "Flexão"]),
        ("corrida resistência aeróbica", ["Corrida", "Ciclismo"]),
    ]

    all_passed = True
    for query, expected_keywords in test_queries:
        results = search_similar(query, top_k=5)
        result_ids = [r["exercicio_id"] for r in results]
        # Buscar nomes
        async with get_db() as conn:
            placeholders = ",".join("?" for _ in result_ids)
            async with conn.execute(
                f"SELECT id, nome FROM exercicios WHERE id IN ({placeholders})",
                result_ids,
            ) as cursor:
                names = {row["id"]: row["nome"] for row in await cursor.fetchall()}

        result_names = [names.get(eid, f"id={eid}") for eid in result_ids]
        logger.info("Query: '%s' → Top-5: %s", query, result_names)

    logger.info("\n✓ Ingestão concluída com sucesso!")
    logger.info("Próximo passo: iniciar a API com 'uvicorn app.main:app --reload'")


if __name__ == "__main__":
    asyncio.run(main())
