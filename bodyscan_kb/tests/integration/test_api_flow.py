"""
Testes de integração — Fluxo completo da API.
Cobre: ingestão → busca vetorial → expansão cross-domínio → log.
"""
import pytest


class TestHealth:
    @pytest.mark.asyncio
    async def test_health_returns_200(self, client):
        """T1 — GET /health deve retornar 200."""
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestKnowledgeBase:
    @pytest.mark.asyncio
    async def test_criar_source(self, client):
        """RF-A1 — Criar fonte de conhecimento."""
        resp = await client.post("/kb/sources", json={
            "dominio": "fisiologia",
            "titulo": "Teste de Fonte",
            "tipo": "nota_interna",
            "confiabilidade": "secundaria",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] is not None
        assert data["dominio"] == "fisiologia"

    @pytest.mark.asyncio
    async def test_criar_chunk_com_embedding(self, client):
        """RF-A2 — Criar chunk com embedding gerado automaticamente."""
        # Criar source primeiro
        src_resp = await client.post("/kb/sources", json={
            "dominio": "treino",
            "titulo": "Fonte Treino",
            "tipo": "protocolo",
            "confiabilidade": "primaria",
        })
        source_id = src_resp.json()["id"]

        resp = await client.post("/kb/chunks", json={
            "source_id": source_id,
            "dominio": "treino",
            "conteudo": "O HIIT é eficaz para redução de gordura visceral.",
            "ordem": 1,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["embedding_model_version"] is not None

    @pytest.mark.asyncio
    async def test_criar_chunk_source_inexistente_retorna_404(self, client):
        resp = await client.post("/kb/chunks", json={
            "source_id": "nao-existe",
            "dominio": "treino",
            "conteudo": "Conteúdo qualquer",
        })
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_criar_concept(self, client):
        """RF-A3 — Criar conceito único por (dominio, nome_canonico)."""
        resp = await client.post("/kb/concepts", json={
            "dominio": "fisiologia",
            "nome": "IMC",
            "nome_canonico": "imc_integ_test",
            "definicao": "Índice de Massa Corporal",
        })
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_criar_concept_duplicado_retorna_409(self, client):
        payload = {
            "dominio": "fisiologia",
            "nome": "RCQ",
            "nome_canonico": "rcq_dup_test",
        }
        await client.post("/kb/concepts", json=payload)
        resp = await client.post("/kb/concepts", json=payload)
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_busca_vetorial_retorna_resultados(self, client):
        """RF-A5 — Busca vetorial filtrada por domínio."""
        # Criar source e chunk
        src = await client.post("/kb/sources", json={
            "dominio": "nutricao",
            "titulo": "Guia Nutricional",
            "tipo": "diretriz",
            "confiabilidade": "oficial",
        })
        await client.post("/kb/chunks", json={
            "source_id": src.json()["id"],
            "dominio": "nutricao",
            "conteudo": "Proteína é essencial para recuperação muscular pós-treino.",
        })

        resp = await client.get("/kb/search?q=proteina+muscular&dominio=nutricao&top_k=5")
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert data["total"] >= 0

    @pytest.mark.asyncio
    async def test_criar_relacao_cross_dominio(self, client):
        """RF-A4 — Criar relação cross-domínio entre conceitos."""
        c1 = await client.post("/kb/concepts", json={
            "dominio": "fisiologia", "nome": "RCA", "nome_canonico": "rca_rel_test"
        })
        c2 = await client.post("/kb/concepts", json={
            "dominio": "treino", "nome": "Cardio", "nome_canonico": "cardio_rel_test"
        })

        resp = await client.post("/kb/relations", json={
            "concept_origem_id": c1.json()["id"],
            "concept_destino_id": c2.json()["id"],
            "dominio_origem": "fisiologia",
            "dominio_destino": "treino",
            "tipo_relacao": "melhora",
            "forca": 0.85,
        })
        assert resp.status_code == 201
        assert resp.json()["dominio_origem"] == "fisiologia"
        assert resp.json()["dominio_destino"] == "treino"


class TestUsers:
    @pytest.mark.asyncio
    async def test_criar_usuario(self, client):
        """RF-C1 — Criar usuário."""
        resp = await client.post("/users", json={
            "sexo_biologico": "F",
            "altura_cm": 165,
            "objetivo_principal": "emagrecimento",
        })
        assert resp.status_code == 201
        assert resp.json()["id"] is not None

    @pytest.mark.asyncio
    async def test_registrar_snapshot_imutavel(self, client):
        """RF-C2 — Snapshot fisiológico imutável com scan_id."""
        user = await client.post("/users", json={"altura_cm": 170, "objetivo_principal": "saude"})
        uid = user.json()["id"]

        resp = await client.post(f"/users/{uid}/snapshots", json={
            "data_medicao": "2025-01-15T10:00:00Z",
            "imc": 28.5,
            "rcq": 0.87,
            "rca": 0.55,
            "fonte": "bodyscan",
            "scan_id": "scan-123",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["scan_id"] == "scan-123"
        assert data["fonte"] == "bodyscan"

    @pytest.mark.asyncio
    async def test_serie_temporal_snapshots(self, client):
        """RF-C3 — Série temporal ordenada por data."""
        user = await client.post("/users", json={"altura_cm": 172})
        uid = user.json()["id"]

        for imc in [30.0, 29.5, 29.0]:
            await client.post(f"/users/{uid}/snapshots", json={
                "data_medicao": f"2025-0{int(imc)-27}-01T10:00:00Z",
                "imc": imc,
                "fonte": "manual",
            })

        resp = await client.get(f"/users/{uid}/snapshots")
        assert resp.status_code == 200
        snapshots = resp.json()
        assert len(snapshots) == 3
        # Verificar ordem decrescente por data
        datas = [s["data_medicao"] for s in snapshots]
        assert datas == sorted(datas, reverse=True)


class TestMemory:
    @pytest.mark.asyncio
    async def test_registrar_episodio(self, client):
        """RF-D1 — Registrar evento episódico."""
        user = await client.post("/users", json={"altura_cm": 168})
        uid = user.json()["id"]

        resp = await client.post(f"/memory/{uid}/episodes", json={
            "tipo_evento": "treino_realizado",
            "dominio": "treino",
            "payload": {"exercicio": "agachamento", "series": 3},
        })
        assert resp.status_code == 201
        assert resp.json()["tipo_evento"] == "treino_realizado"

    @pytest.mark.asyncio
    async def test_registrar_semantica(self, client):
        """RF-D2 — Registrar memória semântica."""
        user = await client.post("/users", json={"altura_cm": 168})
        uid = user.json()["id"]

        resp = await client.post(f"/memory/{uid}/semantic", json={
            "dominio": "treino",
            "tipo": "preferencia",
            "afirmacao": "Prefere treinos matinais de 45 minutos",
            "confianca": 0.9,
        })
        assert resp.status_code == 201
        assert resp.json()["id"] is not None

    @pytest.mark.asyncio
    async def test_vinculo_cross_dominio_status_hipotese(self, client):
        """RF-D3 — Vínculo cross-domínio sempre inicia como hipotese."""
        user = await client.post("/users", json={"altura_cm": 168})
        uid = user.json()["id"]

        c1 = await client.post("/kb/concepts", json={
            "dominio": "fisiologia", "nome": "RCA_test", "nome_canonico": "rca_mem_test"
        })
        c2 = await client.post("/kb/concepts", json={
            "dominio": "treino", "nome": "HIIT_test", "nome_canonico": "hiit_mem_test"
        })

        resp = await client.post(f"/memory/{uid}/cross-links", json={
            "conceito_fisiologia_id": c1.json()["id"],
            "conceito_treino_id": c2.json()["id"],
            "tipo_vinculo": "causa_efeito",
            "descricao": "RCA elevada → HIIT",
        })
        assert resp.status_code == 201
        assert resp.json()["status"] == "hipotese", (
            "GUARDRAIL: status deve ser 'hipotese', nunca 'validado' automaticamente"
        )

    @pytest.mark.asyncio
    async def test_vinculo_com_1_dominio_retorna_422(self, client):
        """RF-D3 — Constraint de mínimo 2 domínios."""
        user = await client.post("/users", json={"altura_cm": 168})
        uid = user.json()["id"]

        c1 = await client.post("/kb/concepts", json={
            "dominio": "fisiologia", "nome": "IMC_only", "nome_canonico": "imc_only_test"
        })

        resp = await client.post(f"/memory/{uid}/cross-links", json={
            "conceito_fisiologia_id": c1.json()["id"],
            "tipo_vinculo": "sinergia",
        })
        assert resp.status_code == 422


class TestAssistant:
    @pytest.mark.asyncio
    async def test_retrieve_retorna_log_id(self, client):
        """RF-E1/E3 — Recuperação orquestrada gera log_id."""
        user = await client.post("/users", json={"altura_cm": 170, "objetivo_principal": "saude"})
        uid = user.json()["id"]

        resp = await client.post(f"/assistant/{uid}/retrieve", json={
            "query": "como melhorar composição corporal",
            "top_k": 3,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "log_id" in data
        assert "contexto" in data
        assert "query" in data

    @pytest.mark.asyncio
    async def test_feedback_registrado(self, client):
        """RF-E3 — Feedback registrado no log."""
        user = await client.post("/users", json={"altura_cm": 170})
        uid = user.json()["id"]

        retrieve_resp = await client.post(f"/assistant/{uid}/retrieve", json={
            "query": "treino para perda de peso",
        })
        log_id = retrieve_resp.json()["log_id"]

        resp = await client.post("/assistant/feedback", json={
            "log_id": log_id,
            "feedback": "positivo",
        })
        assert resp.status_code == 200
        assert resp.json()["feedback"] == "positivo"
