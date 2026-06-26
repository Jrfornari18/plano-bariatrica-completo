# BodyScan KB — Base de Conhecimento com IA Generativa

> Módulo de recomendação educativa para o sistema BodyScan Pós-Bariátrico.
> Implementa RAG (Retrieval-Augmented Generation) com governança clínica completa.

---

## Visão Geral

O **BodyScan KB** é uma API de recomendação baseada em IA generativa que:

1. **Recupera** conhecimento clínico relevante da base vetorial (pgvector)
2. **Filtra** por contexto clínico, nível de evidência e gate de supervisão
3. **Avalia** gatilhos de escalonamento (transtorno alimentar, gestação, uso off-label)
4. **Gera** resposta educativa ancorada nos chunks recuperados via LLM
5. **Audita** toda interação com log completo e conformidade LGPD

---

## Arquitetura

```
Frontend BodyScan (index.html + kb-widget.js)
         │
         ▼ POST /v1/recomendacoes
┌─────────────────────────────────────────┐
│           FastAPI (api/main.py)          │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐ │
│  │ Gate de  │  │Recuperação│  │  LLM  │ │
│  │Escalonam.│→ │ Híbrida  │→ │Geração│ │
│  └──────────┘  └──────────┘  └───────┘ │
│         │            │            │     │
│         └────────────┴────────────┘     │
│                      │                  │
│              ┌───────────────┐          │
│              │   Auditoria   │          │
│              │  (log + LGPD) │          │
│              └───────────────┘          │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     PostgreSQL 16 + pgvector + pg_trgm  │
│                                         │
│  chunk_conhecimento (vector 384/1536)   │
│  recomendacao + evidencia_clinica       │
│  gatilho_escalonamento                  │
│  log_recomendacao + feedback            │
│  perfil_usuario (pseudônimo LGPD)       │
└─────────────────────────────────────────┘
```

---

## Estrutura de Diretórios

```
kb/
├── api/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuração via pydantic-settings
│   ├── database.py          # Pool asyncpg + pgvector
│   ├── middleware/
│   │   └── observabilidade.py  # Logging estruturado + request_id
│   ├── models/
│   │   └── schemas.py       # Pydantic v2 request/response models
│   ├── routers/
│   │   ├── recomendacoes.py # POST /v1/recomendacoes
│   │   ├── conhecimento.py  # GET /v1/conhecimento/buscar
│   │   ├── ingestao.py      # POST /v1/ingestao/documento
│   │   ├── feedback.py      # POST /v1/feedback
│   │   ├── metricas.py      # GET /v1/metricas
│   │   └── lgpd.py          # GET|POST /v1/lgpd/*
│   └── services/
│       ├── embeddings.py    # OpenAI + fallback local
│       ├── recuperacao.py   # Busca vetorial + trigram + regras
│       ├── geracao.py       # LLM com grounding e citação
│       ├── auditoria.py     # Log de recomendações + perfis
│       ├── ingestao.py      # Pipeline de ingestão de documentos
│       └── lgpd.py          # Conformidade LGPD
├── db/
│   ├── schema.sql           # DDL completo (16 tabelas, 2 views, índices HNSW)
│   └── seed_conhecimento.sql # Dados curados de fisiologia do emagrecimento
├── scripts/
│   ├── run_ingestao.py      # Ingestão em batch
│   ├── test_vector_search.py
│   ├── test_m3_recuperacao.py
│   └── test_feedback.py
├── tests/
│   └── test_e2e.py          # 21 testes E2E (todos os critérios de aceite)
├── requirements.txt
├── pytest.ini
├── .env.example
├── .gitignore
└── DEPLOY.md                # Guia completo de deploy
```

---

## Marcos Implementados

| Marco | Descrição | Status |
|---|---|---|
| M0 | PostgreSQL+pgvector, estrutura, CI | ✅ |
| M1 | Schema DDL + seed de conhecimento | ✅ |
| M2 | Pipeline de ingestão + embeddings | ✅ |
| M3 | Recuperação híbrida + camada de regras | ✅ |
| M4 | API FastAPI + gates de governança | ✅ |
| M5 | Integração frontend BodyScan | ✅ |
| M6 | Observabilidade + conformidade LGPD | ✅ |
| M7 | Testes E2E (21/21 passando) | ✅ |
| M8 | Deploy + documentação | ✅ |

---

## Início Rápido

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp .env.example .env  # editar com suas credenciais

# Aplicar banco
psql -d bodyscan_kb -f db/schema.sql
psql -d bodyscan_kb -f db/seed_conhecimento.sql

# Ingerir documentos
python3 scripts/run_ingestao.py

# Iniciar API
python3 -m uvicorn api.main:app --port 8000 --reload

# Testar
curl -X POST http://localhost:8000/v1/recomendacoes \
  -H "Content-Type: application/json" \
  -d '{"pseudonimo":"teste","pergunta":"o que é lipólise?"}'
```

Para instruções completas de deploy, ver [DEPLOY.md](./DEPLOY.md).

---

## Governança Clínica

O sistema implementa múltiplas camadas de segurança:

- **Gate de escalonamento** (RF-07): detecta sinais de transtorno alimentar, gestação, uso off-label e encaminha ao profissional de saúde
- **Gate de supervisão** (RF-08): conteúdo que exige acompanhamento médico não é servido em fluxos autônomos
- **Grounding obrigatório** (RF-06): toda resposta é ancorada nos chunks recuperados, com citação de fontes
- **Aviso educativo**: toda resposta inclui aviso de que não substitui avaliação médica
- **Auditoria completa** (RF-09): todo log inclui hash da resposta, modelo, chunks utilizados e timestamp

---

## Conformidade LGPD

- Sem PII direta — apenas pseudônimo gerado pelo frontend
- Consentimento explícito antes de persistir métricas biométricas
- Endpoints de exportação, revogação e status de consentimento (Art. 18 LGPD)
- Anonimização irreversível ao revogar consentimento

---

## Aviso

Conteúdo de apoio educativo. Não substitui avaliação de médico/nutricionista. Recomendações com
peso clínico exigem supervisão profissional; fontes devem ser verificadas antes de uso em produção.

---

## Licença

Parte integrante do projeto **Barifit.pro** — uso interno.
