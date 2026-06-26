"""
Testes unitários — Serviço de Memória.
Verifica: guardrails, validações, lógica de negócio.
"""
import pytest
from datetime import datetime, timezone

from app.services.memory import MemoryService
from app.schemas.user_memory_schemas import (
    EpisodioCreate,
    SemanticaCreate,
    VinculoCrossCreate,
)
from app.models.l1_knowledge import Concept
from app.models.l3_subject import Usuario


@pytest.fixture
def service():
    return MemoryService()


@pytest.fixture
async def usuario(db_session):
    u = Usuario(
        sexo_biologico="M",
        altura_cm=175,
        objetivo_principal="emagrecimento",
    )
    db_session.add(u)
    await db_session.flush()
    return u


@pytest.fixture
async def conceitos(db_session):
    """Cria conceitos nos três domínios para testes de vínculo."""
    c_fisio = Concept(dominio="fisiologia", nome="IMC", nome_canonico="imc_test")
    c_treino = Concept(dominio="treino", nome="HIIT", nome_canonico="hiit_test")
    c_nutri = Concept(dominio="nutricao", nome="Déficit", nome_canonico="deficit_test")
    for c in [c_fisio, c_treino, c_nutri]:
        db_session.add(c)
    await db_session.flush()
    return {"fisio": c_fisio.id, "treino": c_treino.id, "nutri": c_nutri.id}


class TestMemoriaEpisodica:
    @pytest.mark.asyncio
    async def test_registrar_episodio_sucesso(self, service, db_session, usuario):
        data = EpisodioCreate(
            tipo_evento="scan_corporal",
            dominio="fisiologia",
            payload={"imc": 28.5},
        )
        ep = await service.registrar_episodio(db_session, usuario.id, data)
        assert ep.id is not None
        assert ep.usuario_id == usuario.id
        assert ep.tipo_evento == "scan_corporal"

    @pytest.mark.asyncio
    async def test_listar_episodios_filtrado_por_dominio(self, service, db_session, usuario):
        for dominio in ["fisiologia", "treino", "nutricao"]:
            await service.registrar_episodio(
                db_session, usuario.id,
                EpisodioCreate(tipo_evento="medicao", dominio=dominio)
            )
        fisio = await service.listar_episodios(db_session, usuario.id, dominio="fisiologia")
        assert len(fisio) == 1
        assert fisio[0].dominio == "fisiologia"


class TestMemoriaSemantica:
    @pytest.mark.asyncio
    async def test_registrar_semantica_gera_embedding(self, service, db_session, usuario):
        data = SemanticaCreate(
            dominio="treino",
            tipo="preferencia",
            afirmacao="Responde bem a treino de força 3x/semana",
            confianca=0.85,
        )
        mem = await service.registrar_semantica(db_session, usuario.id, data)
        assert mem.id is not None
        assert mem.embedding is not None
        assert len(mem.embedding) > 0

    @pytest.mark.asyncio
    async def test_listar_semantica_ativa_exclui_inativa(self, service, db_session, usuario):
        await service.registrar_semantica(
            db_session, usuario.id,
            SemanticaCreate(dominio="nutricao", tipo="restricao", afirmacao="Intolerante a lactose", ativo=False)
        )
        await service.registrar_semantica(
            db_session, usuario.id,
            SemanticaCreate(dominio="nutricao", tipo="preferencia", afirmacao="Prefere refeições pequenas", ativo=True)
        )
        ativas = await service.listar_semantica_ativa(db_session, usuario.id)
        assert all(m.ativo for m in ativas)
        assert len(ativas) == 1


class TestVinculoCrossDominio:
    @pytest.mark.asyncio
    async def test_vinculo_sempre_inicia_como_hipotese(self, service, db_session, usuario, conceitos):
        """GUARDRAIL: status nunca deve ser 'validado' automaticamente."""
        data = VinculoCrossCreate(
            conceito_fisiologia_id=conceitos["fisio"],
            conceito_treino_id=conceitos["treino"],
            tipo_vinculo="causa_efeito",
            descricao="RCA elevada → priorizar HIIT",
        )
        vinculo = await service.registrar_vinculo(db_session, usuario.id, data)
        assert vinculo.status == "hipotese", (
            "GUARDRAIL VIOLADO: vínculo cross-domínio não pode ser 'validado' automaticamente"
        )

    @pytest.mark.asyncio
    async def test_vinculo_requer_min_2_dominios(self, service, db_session, usuario, conceitos):
        """RF-D3: constraint de pelo menos 2 domínios."""
        data = VinculoCrossCreate(
            conceito_fisiologia_id=conceitos["fisio"],
            # Apenas 1 domínio — deve falhar
            tipo_vinculo="sinergia",
        )
        with pytest.raises(ValueError, match="pelo menos 2 domínios"):
            await service.registrar_vinculo(db_session, usuario.id, data)

    @pytest.mark.asyncio
    async def test_vinculo_com_3_dominios_aceito(self, service, db_session, usuario, conceitos):
        data = VinculoCrossCreate(
            conceito_fisiologia_id=conceitos["fisio"],
            conceito_treino_id=conceitos["treino"],
            conceito_nutricao_id=conceitos["nutri"],
            tipo_vinculo="sinergia",
            descricao="Todos os três domínios interagem",
        )
        vinculo = await service.registrar_vinculo(db_session, usuario.id, data)
        assert vinculo.id is not None

    @pytest.mark.asyncio
    async def test_listar_vinculos_validados_retorna_apenas_validados(
        self, service, db_session, usuario, conceitos
    ):
        """Apenas vínculos com status='validado' (revisados por humano) devem aparecer."""
        # Criar hipotese
        await service.registrar_vinculo(
            db_session, usuario.id,
            VinculoCrossCreate(
                conceito_fisiologia_id=conceitos["fisio"],
                conceito_treino_id=conceitos["treino"],
                tipo_vinculo="causa_efeito",
            )
        )
        validados = await service.listar_vinculos_validados(db_session, usuario.id)
        # Nenhum deve estar validado (todos iniciam como hipotese)
        assert len(validados) == 0
