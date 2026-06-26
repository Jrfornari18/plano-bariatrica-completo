"""test_vector_search.py — Valida busca vetorial (critério de aceite M2)."""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from api.database import get_pool, close_pool
from api.services.embeddings import embed


async def main():
    pool = await get_pool()
    [vec] = await embed(["proteína pós-bariátrica massa muscular"])
    print(f"Embedding gerado: dim={len(vec)}")

    async with pool.acquire() as con:
        rows = await con.fetch(
            """
            SELECT id, LEFT(texto, 80) AS trecho,
                   embedding <=> $1::vector AS distancia
            FROM chunk_conhecimento
            WHERE nivel_evidencia <> 'nao_verificado'
            ORDER BY embedding <=> $1::vector
            LIMIT 3
            """,
            vec,
        )

    print(f"Busca vetorial retornou {len(rows)} resultados ordenados por distância:")
    for r in rows:
        print(f"  dist={r['distancia']:.4f} | {r['trecho']}...")

    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
