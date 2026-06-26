"""test_feedback.py — Testa endpoint de feedback."""
import asyncio
import httpx

BASE = "http://localhost:8000"


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        # Get a log_id first
        r = await client.post(f"{BASE}/v1/recomendacoes", json={
            "pseudonimo": "teste_feedback_v2",
            "pergunta": "o que é lipólise?",
        })
        data = r.json()
        log_id = data.get("log_id")
        print(f"Log ID obtido: {log_id}")
        print(f"Escalonar: {data.get('escalonar')}")

        if log_id:
            # Submit feedback
            r2 = await client.post(f"{BASE}/v1/feedback", json={
                "log_id": log_id,
                "util": True,
                "comentario": "Muito útil e educativo!",
            })
            print(f"Feedback response: {r2.json()}")

        # Test search endpoint
        r3 = await client.get(f"{BASE}/v1/conhecimento/buscar", params={
            "q": "deficiência vitamínica pós-bariátrico",
            "k": 3,
        })
        busca = r3.json()
        print(f"\nBusca retornou {busca['total']} chunks")
        for c in busca["chunks"]:
            print(f"  dist={c['distancia']:.4f} | {c['texto'][:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
