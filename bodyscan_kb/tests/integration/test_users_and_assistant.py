"""
Testes de integração adicionais — Usuários, Snapshots e Assistente.
Aumenta cobertura dos routers e serviços.
"""
import pytest


class TestUsersExtended:
    @pytest.mark.asyncio
    async def test_usuario_nao_encontrado_retorna_404(self, client):
        resp = await client.get("/users/nao-existe-id")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_snapshot_usuario_inexistente_retorna_404(self, client):
        resp = await client.post("/users/nao-existe/snapshots", json={
            "data_medicao": "2025-01-01T10:00:00Z",
            "fonte": "manual",
        })
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_listar_snapshots_usuario_inexistente_retorna_404(self, client):
        resp = await client.get("/users/nao-existe/snapshots")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_snapshot_campos_opcionais(self, client):
        user = await client.post("/users", json={"altura_cm": 170})
        uid = user.json()["id"]

        resp = await client.post(f"/users/{uid}/snapshots", json={
            "data_medicao": "2025-06-01T08:00:00Z",
            "peso_kg": 75.0,
            "imc": 25.9,
            "perc_gordura": 22.5,
            "risco_cardiovascular": "baixo",
            "fonte": "manual",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["peso_kg"] == 75.0
        assert data["perc_gordura"] == 22.5


class TestAssistantExtended:
    @pytest.mark.asyncio
    async def test_retrieve_usuario_inexistente_retorna_404(self, client):
        resp = await client.post("/assistant/nao-existe/retrieve", json={
            "query": "teste",
        })
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_retrieve_com_dominios_especificos(self, client):
        user = await client.post("/users", json={"altura_cm": 170})
        uid = user.json()["id"]

        resp = await client.post(f"/assistant/{uid}/retrieve", json={
            "query": "proteína para recuperação muscular",
            "dominios": ["nutricao"],
            "top_k": 3,
            "incluir_memoria": False,
            "incluir_cross_dominio": False,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["query"] == "proteína para recuperação muscular"
        assert "log_id" in data

    @pytest.mark.asyncio
    async def test_retrieve_com_memoria_e_cross_dominio(self, client):
        user = await client.post("/users", json={"altura_cm": 170, "objetivo_principal": "emagrecimento"})
        uid = user.json()["id"]

        # Adicionar memória semântica
        await client.post(f"/memory/{uid}/semantic", json={
            "dominio": "treino",
            "tipo": "preferencia",
            "afirmacao": "Prefere treinos de manhã",
            "confianca": 0.9,
        })

        resp = await client.post(f"/assistant/{uid}/retrieve", json={
            "query": "treino para emagrecer",
            "incluir_memoria": True,
            "incluir_cross_dominio": True,
            "top_k": 5,
        })
        assert resp.status_code == 200
        assert "contexto" in resp.json()

    @pytest.mark.asyncio
    async def test_feedback_log_inexistente_retorna_404(self, client):
        resp = await client.post("/assistant/feedback", json={
            "log_id": "log-nao-existe",
            "feedback": "positivo",
        })
        assert resp.status_code == 404


class TestMemoryExtended:
    @pytest.mark.asyncio
    async def test_listar_episodios_vazio(self, client):
        user = await client.post("/users", json={"altura_cm": 170})
        uid = user.json()["id"]
        resp = await client.get(f"/memory/{uid}/episodes")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_listar_semantica_vazia(self, client):
        user = await client.post("/users", json={"altura_cm": 170})
        uid = user.json()["id"]
        resp = await client.get(f"/memory/{uid}/semantic")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_listar_vinculos_vazio(self, client):
        user = await client.post("/users", json={"altura_cm": 170})
        uid = user.json()["id"]
        resp = await client.get(f"/memory/{uid}/cross-links")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_episodio_usuario_inexistente_retorna_404(self, client):
        resp = await client.post("/memory/nao-existe/episodes", json={
            "tipo_evento": "medicao",
            "dominio": "fisiologia",
        })
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_listar_episodios_filtrado_por_dominio(self, client):
        user = await client.post("/users", json={"altura_cm": 170})
        uid = user.json()["id"]

        for dominio in ["fisiologia", "treino", "nutricao"]:
            await client.post(f"/memory/{uid}/episodes", json={
                "tipo_evento": "medicao",
                "dominio": dominio,
            })

        resp = await client.get(f"/memory/{uid}/episodes?dominio=treino")
        assert resp.status_code == 200
        episodios = resp.json()
        assert len(episodios) == 1
        assert episodios[0]["dominio"] == "treino"


class TestKBExtended:
    @pytest.mark.asyncio
    async def test_listar_sources_filtrado_por_dominio(self, client):
        for dominio in ["fisiologia", "treino"]:
            await client.post("/kb/sources", json={
                "dominio": dominio,
                "titulo": f"Fonte {dominio}",
                "tipo": "nota_interna",
                "confiabilidade": "secundaria",
            })

        resp = await client.get("/kb/sources?dominio=treino")
        assert resp.status_code == 200
        sources = resp.json()
        assert all(s["dominio"] == "treino" for s in sources)

    @pytest.mark.asyncio
    async def test_listar_relations_cross_domain_only(self, client):
        c1 = await client.post("/kb/concepts", json={
            "dominio": "fisiologia", "nome": "IMC_cr", "nome_canonico": "imc_cr_test"
        })
        c2 = await client.post("/kb/concepts", json={
            "dominio": "treino", "nome": "HIIT_cr", "nome_canonico": "hiit_cr_test"
        })
        # Relação cross-domínio
        await client.post("/kb/relations", json={
            "concept_origem_id": c1.json()["id"],
            "concept_destino_id": c2.json()["id"],
            "dominio_origem": "fisiologia",
            "dominio_destino": "treino",
            "tipo_relacao": "melhora",
        })

        resp = await client.get("/kb/relations?cross_domain_only=true")
        assert resp.status_code == 200
        relacoes = resp.json()
        for r in relacoes:
            assert r["dominio_origem"] != r["dominio_destino"]
