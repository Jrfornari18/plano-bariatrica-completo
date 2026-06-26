# BodyScan — Motor de Recomendação de Treinos

Backend FastAPI com pipeline RAG híbrido (filtro SQL + busca semântica + geração LLM) para prescrição personalizada de treinos a partir das métricas do BodyScan.

## Arquitetura

```
Perfil do usuário (IMC, RCQ, RCA, objetivo, restrições)
        │
        ▼
[F2] FILTRO ESTRUTURADO (SQL)
     → modalidade, nível, equipamento, exclui contraindicações
        │
        ▼
[F3] BUSCA SEMÂNTICA (FAISS + sentence-transformers)
     → ranqueia candidatos por similaridade com a intenção
        │
        ▼
[F4] GERAÇÃO (LLM configurável via env var)
     → monta treino estruturado + justificativa
        │
        ▼
[F5] VALIDAÇÃO ANTI-ALUCINAÇÃO
     → rejeita exercícios fora do contexto
        │
        ▼
[F6] PERSISTÊNCIA em `recomendacoes`
```

## Setup local

### 1. Instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas credenciais (LLM_API_KEY, etc.)
```

### 3. Gerar índice de embeddings (RF-01)

```bash
python scripts/ingest_embeddings.py
```

### 4. Iniciar a API

```bash
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.
Documentação interativa: `http://localhost:8000/docs`

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Healthcheck |
| `POST` | `/api/v1/recommendations` | Gerar recomendação de treino |
| `POST` | `/api/v1/recommendations/{id}/feedback` | Registrar nota 1–5 |
| `POST` | `/api/v1/profiles` | Criar perfil de usuário |
| `GET` | `/api/v1/profiles/{id}` | Ler perfil |
| `GET` | `/api/v1/exercises` | Listar exercícios (com filtros) |
| `GET` | `/api/v1/exercises/{id}` | Detalhe de exercício |

## Exemplo de requisição

```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "intencao": "quero perder gordura treinando em casa, 30 minutos",
    "modalidades": ["funcional"],
    "nivel": "iniciante",
    "duracao_min": 30,
    "local": "casa",
    "equipamentos_disponiveis": ["Peso corporal"],
    "restricoes": ["lombar"],
    "top_k": 8
  }'
```

## Testes

```bash
# Todos os testes
pytest tests/ -v

# Por módulo
pytest tests/test_filter.py -v           # RF-02: filtro estruturado
pytest tests/test_retrieval.py -v        # RF-03: recuperação semântica
pytest tests/test_anti_hallucination.py -v  # RNF-04: anti-alucinação
pytest tests/test_recommendation_api.py -v  # RF-05: integração ponta a ponta
```

## Variáveis de ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_PATH` | Caminho do banco SQLite | `app/db/knowledge_base.db` |
| `EMBEDDING_MODEL` | Modelo sentence-transformers | `paraphrase-multilingual-MiniLM-L12-v2` |
| `VECTOR_BACKEND` | Backend vetorial | `faiss` |
| `LLM_PROVIDER` | Provider de LLM | `openai_compatible` |
| `LLM_MODEL` | Modelo do LLM | `gpt-4o-mini` |
| `LLM_API_KEY` | Chave da API do LLM | *(obrigatório em produção)* |
| `LLM_BASE_URL` | URL base do provider | *(opcional)* |
| `CORS_ORIGINS` | Origens permitidas pelo CORS | `*` |
| `RATE_LIMIT_PER_MINUTE` | Limite de requisições/min | `30` |

> **Segurança:** Nunca commite o arquivo `.env` ou credenciais no repositório.

## Deploy (Railway)

1. Conectar o repositório ao Railway
2. Configurar as variáveis de ambiente no painel do Railway (especialmente `LLM_API_KEY`)
3. O `railway.json` configura automaticamente o build e o start command

## Disclaimer

> Conteúdo informativo. Não substitui orientação de profissional de saúde ou educação física.
