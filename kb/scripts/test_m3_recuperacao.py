"""
test_m3_recuperacao.py — Valida critérios de aceite do M3.

Aceite:
  1. contexto 'perda_acelerada' + rca>0.5 → recomendação de pele elegível
  2. chunks de supervisão não aparecem quando incluir_supervisao=False
  3. recuperar() retorna top-k filtrado por contexto
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from api.database import get_pool, close_pool
from api.services.recuperacao import (
    recuperar,
    recomendacoes_por_contexto,
    recomendacoes_elegiveis_por_metrica,
    avaliar_condicao_metrica,
    avaliar_gatilhos,
)


async def main():
    pool = await get_pool()
    print("=" * 60)
    print("M3 — Critérios de aceite")
    print("=" * 60)

    # --- Teste 1: RF-05 — rca > 0.5 em perda_acelerada → pele elegível ---
    print("\n[RF-05] Recomendações por contexto 'perda_acelerada':")
    recs = await recomendacoes_por_contexto(pool, "perda_acelerada")
    print(f"  Total de regras: {len(recs)}")
    for r in recs:
        print(f"  - {r.slug} | forca={r.forca} | supervisao={r.requer_supervisao}")
        print(f"    condicao_metrica={r.condicao_metrica}")

    print("\n[RF-05] Com métricas rca=0.6 (> 0.5):")
    metricas = {"rca": 0.6, "imc": 32.0}
    elegiveis = await recomendacoes_elegiveis_por_metrica(
        pool, "perda_acelerada", metricas
    )
    print(f"  Elegíveis: {len(elegiveis)}")
    for r in elegiveis:
        print(f"  ✓ {r.slug} — {r.titulo}")

    # Verifica se há recomendação de pele
    pele_elegivel = any("pele" in r.slug.lower() or "pele" in r.titulo.lower() for r in elegiveis)
    print(f"\n  Recomendação de pele elegível: {'✓ SIM' if pele_elegivel else '✗ NÃO'}")

    # --- Teste 2: RF-08 — chunks de supervisão excluídos sem profissional ---
    print("\n[RF-08] Recuperação sem supervisão (incluir_supervisao=False):")
    chunks = await recuperar(pool, "proteína pós-bariátrica", incluir_supervisao=False)
    supervisao_chunks = [c for c in chunks if c.requer_supervisao]
    print(f"  Chunks recuperados: {len(chunks)}")
    print(f"  Chunks com supervisão incluídos: {len(supervisao_chunks)}")
    print(f"  Gate respeitado: {'✓ SIM' if len(supervisao_chunks) == 0 else '✗ NÃO'}")

    print("\n[RF-08] Recuperação COM supervisão (incluir_supervisao=True):")
    chunks_sup = await recuperar(pool, "proteína pós-bariátrica", incluir_supervisao=True)
    print(f"  Chunks recuperados: {len(chunks_sup)}")

    # --- Teste 3: RF-04 — recuperar() com filtro de contexto ---
    print("\n[RF-04] Recuperação com filtro de contexto 'pos_bariatrico_rygb':")
    chunks_ctx = await recuperar(
        pool,
        "deficiência vitamínica",
        contextos=["pos_bariatrico_rygb"],
        incluir_supervisao=False,
    )
    print(f"  Chunks filtrados por contexto: {len(chunks_ctx)}")
    for c in chunks_ctx:
        print(f"  dist={c.distancia:.4f} | {c.texto[:70]}...")

    # --- Teste 4: Gatilho de escalonamento ---
    print("\n[RF-07] Gatilho de escalonamento:")
    casos = [
        ("quero parar de comer completamente", True),
        ("qual a dose de semaglutida que devo tomar", True),
        ("como aumentar proteína na dieta", False),
    ]
    for texto, esperado_bloqueio in casos:
        gate = await avaliar_gatilhos(pool, texto)
        status = "✓" if gate.bloqueado == esperado_bloqueio else "✗"
        print(f"  {status} '{texto[:50]}...' → bloqueado={gate.bloqueado} tipo={gate.tipo_alerta}")

    print("\n" + "=" * 60)
    print("M3 concluído")
    print("=" * 60)
    await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
