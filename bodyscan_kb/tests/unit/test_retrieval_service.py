"""
Testes unitários — Serviço de Recuperação RAG.
"""
import pytest
from app.services.retrieval import RetrievalService, ChunkResult
from app.services.embedding import MockEmbeddingProvider
from app.models.l1_knowledge import Concept, ConceptRelation, KnowledgeChunk, KnowledgeSource


@pytest.fixture
def service():
    provider = MockEmbeddingProvider(dimension=64)
    return RetrievalService(provider=provider)


@pytest.fixture
async def source_and_chunks(db_session):
    """Cria source e chunks para testes de busca."""
    source = KnowledgeSource(
        dominio="fisiologia",
        titulo="Fonte Teste",
        tipo="nota_interna",
        confiabilidade="secundaria",
    )
    db_session.add(source)
    await db_session.flush()

    provider = MockEmbeddingProvider(dimension=64)
    chunks = []
    for i, texto in enumerate([
        "IMC é calculado pelo peso dividido pela altura ao quadrado",
        "RCA acima de 0.5 indica risco cardiovascular elevado",
        "Percentual de gordura corporal avalia composição corporal",
    ]):
        emb = await provider.embed(texto)
        chunk = KnowledgeChunk(
            source_id=source.id,
            dominio="fisiologia",
            ordem=i + 1,
            conteudo=texto,
            tokens=len(texto.split()),
            embedding=emb,
            embedding_model_version=provider.model_version,
        )
        db_session.add(chunk)
        chunks.append(chunk)

    await db_session.flush()
    return source, chunks


class TestRetrievalService:
    @pytest.mark.asyncio
    async def test_search_retorna_resultados_ordenados(self, service, db_session, source_and_chunks):
        """RF-A5 — Busca retorna top-k ordenados por score."""
        results = await service.search(
            db_session,
            query="IMC e peso corporal",
            dominio="fisiologia",
            top_k=3,
        )
        assert isinstance(results, list)
        # Verificar ordenação decrescente
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].score >= results[i + 1].score

    @pytest.mark.asyncio
    async def test_search_sem_chunks_retorna_lista_vazia(self, service, db_session):
        """Busca sem chunks no banco retorna lista vazia."""
        results = await service.search(db_session, query="qualquer coisa", dominio="treino")
        assert results == []

    @pytest.mark.asyncio
    async def test_search_filtro_dominio(self, service, db_session, source_and_chunks):
        """Filtro por domínio retorna apenas chunks do domínio correto."""
        results = await service.search(
            db_session, query="composição corporal", dominio="treino", top_k=5
        )
        # Não há chunks de treino — deve retornar vazio
        assert results == []

    @pytest.mark.asyncio
    async def test_search_threshold_filtra_resultados(self, service, db_session, source_and_chunks):
        """Threshold alto filtra resultados de baixa similaridade."""
        results_sem_threshold = await service.search(
            db_session, query="IMC", dominio="fisiologia", top_k=5, similarity_threshold=0.0
        )
        results_com_threshold = await service.search(
            db_session, query="IMC", dominio="fisiologia", top_k=5, similarity_threshold=0.99
        )
        # Com threshold alto, menos resultados
        assert len(results_com_threshold) <= len(results_sem_threshold)

    @pytest.mark.asyncio
    async def test_expand_cross_domain_sem_relacoes(self, service, db_session):
        """Expansão sem relações retorna lista vazia."""
        result = await service.expand_cross_domain(db_session, ["id-inexistente"])
        assert result == []

    @pytest.mark.asyncio
    async def test_expand_cross_domain_com_relacoes(self, service, db_session):
        """Expansão retorna relações cross-domínio."""
        c1 = Concept(dominio="fisiologia", nome="RCA", nome_canonico="rca_ret_test")
        c2 = Concept(dominio="treino", nome="HIIT", nome_canonico="hiit_ret_test")
        db_session.add(c1)
        db_session.add(c2)
        await db_session.flush()

        rel = ConceptRelation(
            concept_origem_id=c1.id,
            concept_destino_id=c2.id,
            dominio_origem="fisiologia",
            dominio_destino="treino",
            tipo_relacao="melhora",
            forca=0.8,
        )
        db_session.add(rel)
        await db_session.flush()

        result = await service.expand_cross_domain(db_session, [c1.id])
        assert len(result) == 1
        assert result[0]["dominio_origem"] == "fisiologia"
        assert result[0]["dominio_destino"] == "treino"

    @pytest.mark.asyncio
    async def test_find_concepts_by_text(self, service, db_session):
        """Busca semântica de conceitos."""
        provider = MockEmbeddingProvider(dimension=64)
        emb = await provider.embed("IMC definição")
        c = Concept(
            dominio="fisiologia",
            nome="IMC",
            nome_canonico="imc_find_test",
            embedding=emb,
        )
        db_session.add(c)
        await db_session.flush()

        results = await service.find_concepts_by_text(db_session, "IMC")
        assert len(results) >= 1
        assert results[0]["nome"] == "IMC"
