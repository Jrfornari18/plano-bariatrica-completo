"""
Seeds dos três domínios — T11.
Popula bases de conhecimento (fisiologia, treino, nutrição) e demonstra
expansão cross-domínio com um vínculo de exemplo.

Execução: python seeds/seed_all.py
"""
import asyncio
import sys
import os

# Adicionar raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal, create_all_tables
from app.models.l1_knowledge import Concept, ConceptRelation, KnowledgeChunk, KnowledgeSource
from app.models.l2_domain import (
    FisiologiaMarcador,
    NutricaoAlimento,
    NutricaoProtocolo,
    TreinoExercicio,
    TreinoProtocolo,
)
from app.models.l3_subject import PerfilFisiologicoSnapshot, Usuario
from app.models.l4_memory import MemoriaVinculoCrossDominio
from app.services.embedding import get_embedding_provider


async def seed_fisiologia(db, provider) -> dict[str, str]:
    """Seed do domínio de fisiologia — marcadores IMC, RCQ, RCA, % gordura."""
    print("  → Seeding fisiologia...")

    source = KnowledgeSource(
        dominio="fisiologia",
        titulo="Diretrizes Brasileiras de Obesidade — ABESO 2023",
        tipo="diretriz",
        autor="ABESO",
        referencia="https://abeso.org.br/diretrizes",
        ano=2023,
        confiabilidade="oficial",
        idioma="pt",
    )
    db.add(source)
    await db.flush()

    # Conceitos fisiológicos
    conceitos_fisio = [
        {
            "nome": "Índice de Massa Corporal",
            "nome_canonico": "imc",
            "definicao": "Razão entre peso (kg) e quadrado da altura (m²). Triagem de sobrepeso/obesidade.",
            "tipo_conceito": "marcador",
        },
        {
            "nome": "Relação Cintura-Quadril",
            "nome_canonico": "rcq",
            "definicao": "Razão entre circunferência da cintura e do quadril. Indicador de distribuição de gordura.",
            "tipo_conceito": "marcador",
        },
        {
            "nome": "Relação Cintura-Altura",
            "nome_canonico": "rca",
            "definicao": "Razão entre circunferência da cintura e altura. Preditor de risco cardiometabólico.",
            "tipo_conceito": "marcador",
        },
        {
            "nome": "Percentual de Gordura Corporal",
            "nome_canonico": "perc_gordura",
            "definicao": "Proporção de massa gorda em relação à massa corporal total.",
            "tipo_conceito": "marcador",
        },
    ]

    concept_ids = {}
    for c_data in conceitos_fisio:
        emb = await provider.embed(f"{c_data['nome']}: {c_data['definicao']}")
        concept = Concept(
            dominio="fisiologia",
            tipo_conceito=c_data["tipo_conceito"],
            nome=c_data["nome"],
            nome_canonico=c_data["nome_canonico"],
            definicao=c_data["definicao"],
            embedding=emb,
        )
        db.add(concept)
        await db.flush()
        concept_ids[c_data["nome_canonico"]] = concept.id

    # Marcadores fisiológicos com faixas de referência
    marcadores = [
        {
            "concept_id": concept_ids["imc"],
            "unidade": "kg/m²",
            "categoria": "antropometrico",
            "faixa_ref_min": 18.5,
            "faixa_ref_max": 24.9,
            "estratificacao": {
                "adulto": {
                    "abaixo_peso": {"max": 18.4},
                    "normal": {"min": 18.5, "max": 24.9},
                    "sobrepeso": {"min": 25.0, "max": 29.9},
                    "obesidade_1": {"min": 30.0, "max": 34.9},
                    "obesidade_2": {"min": 35.0, "max": 39.9},
                    "obesidade_3": {"min": 40.0},
                }
            },
        },
        {
            "concept_id": concept_ids["rcq"],
            "unidade": "ratio",
            "categoria": "cardiovascular",
            "faixa_ref_min": None,
            "faixa_ref_max": None,
            "estratificacao": {
                "homem": {"risco_elevado": {"min": 0.90}},
                "mulher": {"risco_elevado": {"min": 0.85}},
            },
        },
        {
            "concept_id": concept_ids["rca"],
            "unidade": "ratio",
            "categoria": "cardiovascular",
            "faixa_ref_min": None,
            "faixa_ref_max": 0.50,
            "estratificacao": {
                "adulto": {
                    "normal": {"max": 0.50},
                    "risco_elevado": {"min": 0.50, "max": 0.60},
                    "risco_muito_elevado": {"min": 0.60},
                }
            },
        },
        {
            "concept_id": concept_ids["perc_gordura"],
            "unidade": "%",
            "categoria": "composicao_corporal",
            "estratificacao": {
                "homem": {
                    "atleta": {"max": 13},
                    "bom": {"min": 14, "max": 17},
                    "aceitavel": {"min": 18, "max": 24},
                    "obesidade": {"min": 25},
                },
                "mulher": {
                    "atleta": {"max": 20},
                    "bom": {"min": 21, "max": 24},
                    "aceitavel": {"min": 25, "max": 31},
                    "obesidade": {"min": 32},
                },
            },
        },
    ]
    for m in marcadores:
        db.add(FisiologiaMarcador(**m))

    # Chunks de conhecimento
    chunks_fisio = [
        "O IMC é calculado dividindo o peso em quilogramas pelo quadrado da altura em metros. Valores entre 18,5 e 24,9 kg/m² são considerados normais para adultos.",
        "A RCA (relação cintura-altura) acima de 0,5 indica risco cardiometabólico elevado, independentemente do IMC. É especialmente útil em populações com IMC limítrofe.",
        "O percentual de gordura corporal é mais preciso que o IMC para avaliar composição corporal, pois distingue massa magra de massa gorda.",
        "Pacientes pós-bariátrica frequentemente apresentam IMC normalizado mas ainda podem ter distribuição de gordura visceral elevada, tornando RCQ e RCA métricas mais relevantes.",
    ]
    for i, conteudo in enumerate(chunks_fisio):
        emb = await provider.embed(conteudo)
        db.add(KnowledgeChunk(
            source_id=source.id,
            dominio="fisiologia",
            ordem=i + 1,
            conteudo=conteudo,
            tokens=len(conteudo.split()),
            embedding=emb,
            embedding_model_version=provider.model_version,
        ))

    await db.flush()
    print(f"    ✓ {len(conceitos_fisio)} conceitos, {len(chunks_fisio)} chunks")
    return concept_ids


async def seed_treino(db, provider) -> dict[str, str]:
    """Seed do domínio de treino — exercícios e protocolos."""
    print("  → Seeding treino...")

    source = KnowledgeSource(
        dominio="treino",
        titulo="Princípios de Treinamento para Populações Especiais — ACSM 2022",
        tipo="livro",
        autor="American College of Sports Medicine",
        ano=2022,
        confiabilidade="primaria",
        idioma="en",
    )
    db.add(source)
    await db.flush()

    conceitos_treino = [
        {
            "nome": "HIIT — Treinamento Intervalado de Alta Intensidade",
            "nome_canonico": "hiit",
            "definicao": "Alternância entre períodos de esforço máximo e recuperação ativa. Eficaz para perda de gordura e melhora cardiovascular.",
            "tipo_conceito": "protocolo_treino",
        },
        {
            "nome": "Agachamento",
            "nome_canonico": "agachamento",
            "definicao": "Exercício multiarticular de membros inferiores. Padrão de movimento: agachar.",
            "tipo_conceito": "exercicio",
        },
        {
            "nome": "Caminhada em Esteira",
            "nome_canonico": "caminhada_esteira",
            "definicao": "Exercício aeróbico de baixo impacto. Ideal para iniciantes e pós-operatório.",
            "tipo_conceito": "exercicio",
        },
    ]

    concept_ids = {}
    for c_data in conceitos_treino:
        emb = await provider.embed(f"{c_data['nome']}: {c_data['definicao']}")
        concept = Concept(
            dominio="treino",
            tipo_conceito=c_data["tipo_conceito"],
            nome=c_data["nome"],
            nome_canonico=c_data["nome_canonico"],
            definicao=c_data["definicao"],
            embedding=emb,
        )
        db.add(concept)
        await db.flush()
        concept_ids[c_data["nome_canonico"]] = concept.id

    # Exercícios especializados
    db.add(TreinoExercicio(
        concept_id=concept_ids["agachamento"],
        padrao_movimento="agachar",
        grupo_muscular_primario=["quadriceps", "gluteos"],
        grupo_muscular_secundario=["isquiotibiais", "core"],
        equipamento="barra ou peso corporal",
        tipo="forca",
        nivel="iniciante",
    ))
    db.add(TreinoExercicio(
        concept_id=concept_ids["caminhada_esteira"],
        padrao_movimento="locomocao",
        grupo_muscular_primario=["quadriceps", "gluteos", "panturrilha"],
        equipamento="esteira",
        tipo="cardio",
        nivel="iniciante",
    ))

    # Protocolos de treino
    db.add(TreinoProtocolo(
        nome="HIIT 20/40",
        objetivo="Queima de gordura e condicionamento cardiovascular",
        variaveis={
            "series": 8,
            "tempo_esforco_s": 20,
            "tempo_recuperacao_s": 40,
            "frequencia_semanal": 3,
            "duracao_total_min": 20,
        },
    ))
    db.add(TreinoProtocolo(
        nome="Força Progressiva 3x10",
        objetivo="Hipertrofia e ganho de força para iniciantes",
        variaveis={
            "series": 3,
            "repeticoes": 10,
            "descanso_s": 90,
            "frequencia_semanal": 3,
            "progressao": "adicionar 2.5kg quando completar todas as séries",
        },
    ))

    # Chunks de conhecimento
    chunks_treino = [
        "O HIIT (High-Intensity Interval Training) é eficaz para redução de gordura visceral em pacientes com obesidade. Estudos mostram redução de até 17% em 12 semanas com 3 sessões semanais.",
        "Para pacientes pós-bariátrica, o treinamento de força é essencial para preservar massa muscular durante a perda de peso acelerada. Recomenda-se iniciar com exercícios de peso corporal.",
        "A caminhada é o exercício mais acessível e seguro para iniciantes pós-cirurgia. Iniciar com 10-15 minutos e progredir gradualmente até 30-45 minutos diários.",
        "O treinamento de força 3x/semana com progressão de carga demonstra melhora significativa na composição corporal e sensibilidade à insulina em populações com sobrepeso.",
    ]
    for i, conteudo in enumerate(chunks_treino):
        emb = await provider.embed(conteudo)
        db.add(KnowledgeChunk(
            source_id=source.id,
            dominio="treino",
            ordem=i + 1,
            conteudo=conteudo,
            tokens=len(conteudo.split()),
            embedding=emb,
            embedding_model_version=provider.model_version,
        ))

    await db.flush()
    print(f"    ✓ {len(conceitos_treino)} conceitos, {len(chunks_treino)} chunks")
    return concept_ids


async def seed_nutricao(db, provider) -> dict[str, str]:
    """Seed do domínio de nutrição — alimentos e protocolos."""
    print("  → Seeding nutrição...")

    source = KnowledgeSource(
        dominio="nutricao",
        titulo="Guia Alimentar para a População Brasileira — MS 2014",
        tipo="diretriz",
        autor="Ministério da Saúde",
        ano=2014,
        confiabilidade="oficial",
        idioma="pt",
    )
    db.add(source)
    await db.flush()

    conceitos_nutricao = [
        {
            "nome": "Proteína Whey",
            "nome_canonico": "proteina_whey",
            "definicao": "Proteína do soro do leite de alta biodisponibilidade. Suplemento comum para recuperação muscular.",
            "tipo_conceito": "alimento",
        },
        {
            "nome": "Déficit Calórico",
            "nome_canonico": "deficit_calorico",
            "definicao": "Estado em que o consumo calórico é inferior ao gasto energético total. Necessário para perda de peso.",
            "tipo_conceito": "protocolo_nutricional",
        },
        {
            "nome": "Proteína Dietética",
            "nome_canonico": "proteina_dietetica",
            "definicao": "Macronutriente essencial para síntese muscular. Recomendação: 1,6-2,2g/kg/dia para atletas.",
            "tipo_conceito": "macronutriente",
        },
    ]

    concept_ids = {}
    for c_data in conceitos_nutricao:
        emb = await provider.embed(f"{c_data['nome']}: {c_data['definicao']}")
        concept = Concept(
            dominio="nutricao",
            tipo_conceito=c_data["tipo_conceito"],
            nome=c_data["nome"],
            nome_canonico=c_data["nome_canonico"],
            definicao=c_data["definicao"],
            embedding=emb,
        )
        db.add(concept)
        await db.flush()
        concept_ids[c_data["nome_canonico"]] = concept.id

    # Alimento especializado
    db.add(NutricaoAlimento(
        concept_id=concept_ids["proteina_whey"],
        categoria="suplemento",
        kcal_por_100g=380,
        macros={"proteina_g": 80, "carboidrato_g": 5, "gordura_g": 4, "fibra_g": 0},
        micronutrientes={"calcio_mg": 120, "sodio_mg": 150},
    ))

    # Protocolos nutricionais
    db.add(NutricaoProtocolo(
        nome="Low Carb Moderado",
        objetivo="Perda de gordura com preservação de massa muscular",
        restricoes={
            "carboidratos_max_g_dia": 100,
            "proteina_min_g_kg": 1.8,
            "gordura_perc_calorias": 35,
        },
    ))
    db.add(NutricaoProtocolo(
        nome="Dieta Pós-Bariátrica Fase 3",
        objetivo="Reintrodução alimentar progressiva pós-cirurgia",
        restricoes={
            "textura": "pastosa_a_solida",
            "refeicoes_por_dia": 6,
            "volume_max_ml_por_refeicao": 200,
            "evitar": ["bebidas_carbonatadas", "alimentos_muito_gordurosos"],
        },
    ))

    # Chunks de conhecimento
    chunks_nutricao = [
        "A ingestão proteica adequada (1,6-2,2g/kg/dia) é fundamental para preservar massa muscular durante déficit calórico. Pacientes pós-bariátrica têm maior risco de sarcopenia.",
        "O déficit calórico de 500-750 kcal/dia promove perda de peso de 0,5-0,75 kg/semana sem comprometer o metabolismo basal em adultos saudáveis.",
        "Pacientes pós-bariátrica devem priorizar alimentos proteicos em cada refeição antes de consumir carboidratos, para otimizar absorção e saciedade.",
        "A suplementação com proteína whey pós-treino aumenta a síntese proteica muscular em até 25% comparado ao consumo em outros momentos do dia.",
    ]
    for i, conteudo in enumerate(chunks_nutricao):
        emb = await provider.embed(conteudo)
        db.add(KnowledgeChunk(
            source_id=source.id,
            dominio="nutricao",
            ordem=i + 1,
            conteudo=conteudo,
            tokens=len(conteudo.split()),
            embedding=emb,
            embedding_model_version=provider.model_version,
        ))

    await db.flush()
    print(f"    ✓ {len(conceitos_nutricao)} conceitos, {len(chunks_nutricao)} chunks")
    return concept_ids


async def seed_cross_domain_relations(
    db,
    fisio_ids: dict,
    treino_ids: dict,
    nutricao_ids: dict,
):
    """
    Seed de relações cross-domínio no grafo de conceitos.
    Demonstra a expansão cross-domínio do PRD.
    """
    print("  → Seeding relações cross-domínio...")

    relacoes = [
        # RCA elevada → priorizar HIIT (fisiologia → treino)
        {
            "concept_origem_id": fisio_ids["rca"],
            "concept_destino_id": treino_ids["hiit"],
            "dominio_origem": "fisiologia",
            "dominio_destino": "treino",
            "tipo_relacao": "melhora",
            "forca": 0.85,
            "direcional": True,
        },
        # IMC elevado → déficit calórico (fisiologia → nutrição)
        {
            "concept_origem_id": fisio_ids["imc"],
            "concept_destino_id": nutricao_ids["deficit_calorico"],
            "dominio_origem": "fisiologia",
            "dominio_destino": "nutricao",
            "tipo_relacao": "requer",
            "forca": 0.90,
            "direcional": True,
        },
        # Treino de força → proteína dietética (treino → nutrição)
        {
            "concept_origem_id": treino_ids["agachamento"],
            "concept_destino_id": nutricao_ids["proteina_dietetica"],
            "dominio_origem": "treino",
            "dominio_destino": "nutricao",
            "tipo_relacao": "requer",
            "forca": 0.80,
            "direcional": True,
        },
    ]

    for r in relacoes:
        db.add(ConceptRelation(**r))

    await db.flush()
    print(f"    ✓ {len(relacoes)} relações cross-domínio")


async def seed_usuario_exemplo(
    db,
    fisio_ids: dict,
    treino_ids: dict,
    nutricao_ids: dict,
) -> str:
    """Seed de usuário exemplo com snapshot e vínculo cross-domínio."""
    print("  → Seeding usuário exemplo...")

    from datetime import date, datetime, timezone

    usuario = Usuario(
        sexo_biologico="F",
        data_nascimento=date(1985, 6, 15),
        altura_cm=165,
        objetivo_principal="emagrecimento",
        nivel_atividade="moderado",
        restricoes={"condicoes": ["pos_bariatrica_12_meses"], "alergias": []},
    )
    db.add(usuario)
    await db.flush()

    # Snapshot fisiológico (simulando saída do BodyScan)
    snapshot = PerfilFisiologicoSnapshot(
        usuario_id=usuario.id,
        scan_id="scan-exemplo-001",
        data_medicao=datetime.now(timezone.utc),
        peso_kg=82.5,
        imc=30.3,
        circ_cintura=95.0,
        circ_quadril=108.0,
        circ_ombro=112.0,
        rcq=0.88,
        rca=0.576,
        perc_gordura=38.2,
        risco_cardiovascular="moderado",
        fonte="bodyscan",
    )
    db.add(snapshot)
    await db.flush()

    # Vínculo cross-domínio de exemplo (status=hipotese — GUARDRAIL)
    vinculo = MemoriaVinculoCrossDominio(
        usuario_id=usuario.id,
        conceito_fisiologia_id=fisio_ids["rca"],
        conceito_treino_id=treino_ids["hiit"],
        conceito_nutricao_id=nutricao_ids["deficit_calorico"],
        tipo_vinculo="causa_efeito",
        descricao=(
            "RCA=0,576 (risco elevado) + déficit calórico atual "
            "⇒ priorizar HIIT para redução de gordura visceral"
        ),
        forca=0.82,
        gerado_por="regra",
        evidencia={"snapshot_id": snapshot.id, "rca_valor": 0.576},
        status="hipotese",  # GUARDRAIL: nunca 'validado' automaticamente
    )
    db.add(vinculo)
    await db.flush()

    print(f"    ✓ Usuário {usuario.id} com snapshot e vínculo cross-domínio (hipotese)")
    return usuario.id


async def main():
    print("BodyScan KB & Memory — Seed dos três domínios")
    print("=" * 55)

    await create_all_tables()
    provider = get_embedding_provider()

    async with AsyncSessionLocal() as db:
        try:
            fisio_ids = await seed_fisiologia(db, provider)
            treino_ids = await seed_treino(db, provider)
            nutricao_ids = await seed_nutricao(db, provider)
            await seed_cross_domain_relations(db, fisio_ids, treino_ids, nutricao_ids)
            usuario_id = await seed_usuario_exemplo(db, fisio_ids, treino_ids, nutricao_ids)
            await db.commit()
            print("\n✅ Seed concluído com sucesso!")
            print(f"   Usuário de exemplo: {usuario_id}")
            print("\nPróximo passo: testar expansão cross-domínio via GET /kb/relations?cross_domain_only=true")
        except Exception as e:
            await db.rollback()
            print(f"\n❌ Erro no seed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
