# BodyScan KB & Memory — Módulo de Base de Conhecimento e Memória

Módulo backend Python (FastAPI + SQLAlchemy async) que implementa a **Base de Conhecimento** e o **Sistema de Memória Personalizada** do assistente BodyScan/Barifit.pro, conforme especificado no PRD `PRD_kb_memoria_manus.md`.

---

## Arquitetura em Camadas (L1–L5)

```
L1 — Conhecimento de Domínio     knowledge_source, knowledge_chunk, concept, concept_relation
L2 — Especializações             fisiologia_marcador, treino_exercicio, treino_protocolo,
                                 nutricao_alimento, nutricao_protocolo
L3 — Sujeito (Usuário)           usuario, perfil_fisiologico_snapshot
L4 — Memória Personalizada       memoria_episodica, memoria_semantica,
                                 memoria_vinculo_cross_dominio, contexto_sessao
L5 — Orquestração / Log          recuperacao_log
```

---

## Estrutura de Pastas

```
bodyscan_kb/
├── app/
│   ├── api/
│   │   ├── assistant_router.py   # Épico E — orquestração de recuperação
│   │   ├── kb_router.py          # Épicos A + B — base de conhecimento
│   │   ├── memory_router.py      # Épico D — memória personalizada
│   │   └── users_router.py       # Épico C — usuários e snapshots
│   ├── core/
│   │   ├── config.py             # Pydantic-settings — variáveis de ambiente
│   │   ├── database.py           # Engine async + sessão
│   │   └── logging.py            # Logging estruturado
│   ├── models/
│   │   ├── l1_knowledge.py       # ORM — L1
│   │   ├── l2_domain.py          # ORM — L2
│   │   ├── l3_subject.py         # ORM — L3
│   │   ├── l4_memory.py          # ORM — L4
│   │   └── l5_retrieval.py       # ORM — L5
│   ├── schemas/
│   │   ├── kb_schemas.py         # Pydantic v2 — KB
│   │   └── user_memory_schemas.py # Pydantic v2 — Usuário/Memória
│   ├── services/
│   │   ├── assistant.py          # Orquestrador RAG + memória
│   │   ├── embedding.py          # EmbeddingProvider (mock/ST/OpenAI)
│   │   ├── memory.py             # Serviço de memória
│   │   └── retrieval.py          # Busca vetorial + expansão cross-domínio
│   └── main.py                   # Aplicação FastAPI + health endpoint
├── migrations/
│   ├── env.py                    # Alembic async
│   ├── script.py.mako
│   └── versions/
│       └── 001_initial_schema.py # Migração inicial L1–L5 (upgrade + downgrade)
├── seeds/
│   └── seed_all.py               # Seeds dos 3 domínios + vínculo cross-domínio
├── tests/
│   ├── conftest.py               # Fixtures async com banco em memória
│   ├── integration/
│   │   ├── test_api_flow.py      # Fluxo completo da API
│   │   ├── test_migration.py     # Regressão de migrações
│   │   └── test_users_and_assistant.py
│   └── unit/
│       ├── test_embedding.py     # EmbeddingProvider + similaridade cosseno
│       ├── test_memory_service.py # Guardrails + validações de negócio
│       └── test_retrieval_service.py # RAG + expansão cross-domínio
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── requirements.txt
└── .env.example
```

---

## Instalação e Execução

### Pré-requisitos

- Python 3.11+
- (Opcional) Docker

### Configuração local

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Copiar e configurar variáveis de ambiente
cp .env.example .env
# Editar .env conforme necessário

# 3. Executar migrações
alembic upgrade head

# 4. Popular base de conhecimento com seeds
python seeds/seed_all.py

# 5. Iniciar servidor de desenvolvimento
uvicorn app.main:app --reload --port 8000
```

### Via Docker

```bash
docker-compose up
```

A API estará disponível em `http://localhost:8000`.

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./bodyscan_kb.db` | URL do banco (SQLite MVP / PostgreSQL produção) |
| `EMBEDDING_PROVIDER` | `mock` | Provider de embeddings: `mock`, `sentence_transformers`, `openai` |
| `EMBEDDING_DIMENSION` | `384` | Dimensão dos vetores |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Modelo sentence-transformers |
| `OPENAI_API_KEY` | — | Chave OpenAI (apenas se `EMBEDDING_PROVIDER=openai`) |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `CORS_ORIGINS` | `*` | Origens CORS permitidas |

---

## Endpoints da API

### Health

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Status do serviço e versão |

### Base de Conhecimento (`/kb`)

| Método | Rota | RF | Descrição |
|---|---|---|---|
| `POST` | `/kb/sources` | RF-A1 | Criar fonte de conhecimento |
| `GET` | `/kb/sources` | — | Listar fontes (filtro por domínio) |
| `POST` | `/kb/chunks` | RF-A2 | Criar chunk com embedding automático |
| `POST` | `/kb/concepts` | RF-A3 | Criar conceito único por (domínio, nome_canônico) |
| `GET` | `/kb/concepts` | — | Listar conceitos |
| `POST` | `/kb/relations` | RF-A4 | Criar relação intra/cross-domínio |
| `GET` | `/kb/relations` | — | Listar relações (filtro cross-domain) |
| `GET` | `/kb/search` | RF-A5 | Busca vetorial por domínio |
| `POST` | `/kb/domain/fisiologia-marcador` | RF-B1 | Criar marcador fisiológico |
| `POST` | `/kb/domain/treino-exercicio` | RF-B1 | Criar exercício |
| `POST` | `/kb/domain/treino-protocolo` | RF-B2 | Criar protocolo de treino |
| `POST` | `/kb/domain/nutricao-alimento` | RF-B1 | Criar alimento |
| `POST` | `/kb/domain/nutricao-protocolo` | RF-B2 | Criar protocolo nutricional |

### Usuários (`/users`)

| Método | Rota | RF | Descrição |
|---|---|---|---|
| `POST` | `/users` | RF-C1 | Criar usuário |
| `GET` | `/users/{id}` | — | Obter usuário |
| `POST` | `/users/{id}/snapshots` | RF-C2 | Registrar snapshot fisiológico (imutável) |
| `GET` | `/users/{id}/snapshots` | RF-C3 | Série temporal de snapshots |

### Memória (`/memory`)

| Método | Rota | RF | Descrição |
|---|---|---|---|
| `POST` | `/memory/{id}/episodes` | RF-D1 | Registrar evento episódico |
| `GET` | `/memory/{id}/episodes` | — | Listar episódios |
| `POST` | `/memory/{id}/semantic` | RF-D2 | Registrar memória semântica |
| `GET` | `/memory/{id}/semantic` | — | Listar memórias ativas |
| `POST` | `/memory/{id}/cross-links` | RF-D3 | Registrar vínculo cross-domínio |
| `GET` | `/memory/{id}/cross-links` | — | Listar vínculos |

### Assistente (`/assistant`)

| Método | Rota | RF | Descrição |
|---|---|---|---|
| `POST` | `/assistant/{id}/retrieve` | RF-E1/E2/E3 | Recuperação orquestrada completa |
| `POST` | `/assistant/feedback` | RF-E3 | Registrar feedback em log |

---

## Guardrails de Segurança

O módulo implementa os seguintes guardrails definidos no PRD:

**Vínculos cross-domínio** (`memoria_vinculo_cross_dominio`) sempre iniciam com `status = "hipotese"`. A transição para `"validado"` exige revisão humana explícita — nunca ocorre automaticamente. Isso é verificado por testes unitários dedicados (`test_vinculo_sempre_inicia_como_hipotese`).

**Snapshots fisiológicos** são imutáveis após criação. Não há endpoint de atualização, garantindo integridade da série temporal.

**Vínculos cross-domínio** exigem pelo menos 2 domínios preenchidos (constraint `ck_mvcd_min_2_dominios` no banco + validação no serviço).

---

## Testes

```bash
# Executar todos os testes com cobertura
pytest

# Apenas testes unitários
pytest tests/unit/ -v

# Apenas testes de integração
pytest tests/integration/ -v
```

**Resultado esperado:** 62 testes passando, cobertura ≥ 79%.

---

## Migrações Alembic

```bash
# Aplicar todas as migrações
alembic upgrade head

# Reverter última migração
alembic downgrade -1

# Verificar estado atual
alembic current

# Gerar nova migração automática
alembic revision --autogenerate -m "descricao_da_mudanca"
```

---

## Integração com BodyScan

O campo `scan_id` em `perfil_fisiologico_snapshot` vincula cada snapshot ao resultado de um scan corporal do BodyScan. O endpoint `POST /assistant/{id}/retrieve` retorna automaticamente o snapshot mais recente do usuário como parte do contexto, permitindo que o assistente personalize respostas com base nos dados biométricos atuais.

---

## Roadmap

| Fase | Descrição |
|---|---|
| MVP (atual) | SQLite + embeddings mock + busca por similaridade cosseno |
| v1.0 | PostgreSQL + pgvector + sentence-transformers local |
| v1.1 | OpenAI embeddings + cache Redis |
| v2.0 | Grafo de conceitos com Neo4j + expansão multi-hop |
