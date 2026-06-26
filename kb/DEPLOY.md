# BodyScan KB — Guia de Deploy e Operação

> **Versão:** 1.0.0 | **Ambiente mínimo:** Ubuntu 22.04+ / Debian 12+

---

## Sumário

1. [Pré-requisitos](#1-pré-requisitos)
2. [Instalação local (desenvolvimento)](#2-instalação-local-desenvolvimento)
3. [Variáveis de ambiente](#3-variáveis-de-ambiente)
4. [Banco de dados](#4-banco-de-dados)
5. [Ingestão de documentos](#5-ingestão-de-documentos)
6. [Executar a API](#6-executar-a-api)
7. [Integração com o frontend BodyScan](#7-integração-com-o-frontend-bodyscan)
8. [Deploy em produção (Docker)](#8-deploy-em-produção-docker)
9. [Endpoints da API](#9-endpoints-da-api)
10. [Observabilidade](#10-observabilidade)
11. [Conformidade LGPD](#11-conformidade-lgpd)
12. [Testes](#12-testes)
13. [Notas de segurança](#13-notas-de-segurança)

---

## 1. Pré-requisitos

| Componente | Versão mínima | Notas |
|---|---|---|
| Python | 3.11+ | `python3 --version` |
| PostgreSQL | 15+ | Com extensão `pgvector` |
| pgvector | 0.5+ | `CREATE EXTENSION vector;` |
| OpenAI API Key | — | Para embeddings `text-embedding-3-small` (dim=1536) |
| Sentence-Transformers | — | Fallback local `all-MiniLM-L6-v2` (dim=384) |

---

## 2. Instalação local (desenvolvimento)

```bash
# 1. Clonar o repositório
git clone https://github.com/Jrfornari18/plano-bariatrica-completo.git
cd plano-bariatrica-completo/kb

# 2. Instalar dependências Python
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# 4. Instalar PostgreSQL + pgvector (Ubuntu/Debian)
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y postgresql-16-pgvector  # ajustar versão

# 5. Criar banco de dados
sudo -u postgres createdb bodyscan_kb
sudo -u postgres psql -d bodyscan_kb -c "CREATE EXTENSION IF NOT EXISTS vector;"
sudo -u postgres psql -d bodyscan_kb -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
sudo -u postgres psql -d bodyscan_kb -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"

# 6. Aplicar schema e seed
sudo -u postgres psql -d bodyscan_kb -f db/schema.sql
sudo -u postgres psql -d bodyscan_kb -f db/seed_conhecimento.sql

# 7. Executar pipeline de ingestão (gera embeddings)
python3 scripts/run_ingestao.py

# 8. Iniciar API
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 3. Variáveis de ambiente

Copiar `.env.example` para `.env` e preencher:

```env
# Banco de dados
DATABASE_URL=postgresql://postgres:senha@localhost:5432/bodyscan_kb

# OpenAI (para embeddings text-embedding-3-small e chat)
OPENAI_API_KEY=sk-...
OPENAI_EMBED_MODEL=text-embedding-3-small   # dim=1536 em produção
OPENAI_CHAT_MODEL=gpt-4o-mini

# API
API_ENV=production   # development | production
API_HOST=0.0.0.0
API_PORT=8000

# Embedding local (fallback quando OpenAI indisponível)
# EMBED_MODEL_LOCAL=all-MiniLM-L6-v2
# EMBED_DIM=384
```

> **Atenção:** Em produção com `text-embedding-3-small`, o schema usa `vector(1536)`.
> Em desenvolvimento com modelo local, o schema usa `vector(384)`.
> **Não misture dimensões** — recriar o banco se trocar de modelo.

---

## 4. Banco de dados

### Estrutura principal

| Tabela | Descrição |
|---|---|
| `documento_conhecimento` | Documentos fonte (PDFs, artigos) |
| `chunk_conhecimento` | Chunks com embedding vetorial |
| `dominio_clinico` | Domínios (nutrição, exercício, etc.) |
| `contexto_clinico` | Contextos (pós-RYGB, perda acelerada, etc.) |
| `recomendacao` | Recomendações com condições de elegibilidade |
| `evidencia_clinica` | Referências bibliográficas |
| `gatilho_escalonamento` | Padrões de texto que ativam escalonamento |
| `perfil_usuario` | Pseudônimos + consentimento LGPD |
| `perfil_metrica` | Métricas biométricas por perfil |
| `log_recomendacao` | Auditoria de todas as recomendações |
| `feedback_recomendacao` | Feedback dos usuários |

### Views

| View | Descrição |
|---|---|
| `vw_chunk_servivel` | Chunks com evidência verificada (excl. `nao_verificado`) |
| `vw_recomendacao_com_evidencia` | Recomendações com referência bibliográfica |

### Backup

```bash
pg_dump -U postgres bodyscan_kb > backup_$(date +%Y%m%d).sql
```

---

## 5. Ingestão de documentos

### Via script (batch)

```bash
cd kb/
python3 scripts/run_ingestao.py
```

### Via API (individual)

```bash
curl -X POST http://localhost:8000/v1/ingestao/documento \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Guia Nutricional Pós-Bariátrico",
    "conteudo": "Texto completo do documento...",
    "dominio_slug": "nutricao",
    "contexto_slugs": ["pos_rygb_0_12m"],
    "nivel_evidencia": "revisao_sistematica",
    "requer_supervisao_medica": false
  }'
```

---

## 6. Executar a API

### Desenvolvimento

```bash
cd kb/
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
```

### Produção (com workers)

```bash
python3 -m uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level warning \
  --access-log
```

### Verificar saúde

```bash
curl http://localhost:8000/health
# {"status": "ok", "env": "production", "embed_dim": 1536}
```

---

## 7. Integração com o frontend BodyScan

O widget KB já está integrado ao `index.html`. Para configurar a URL da API:

```html
<!-- Em index.html, antes de kb-widget.js -->
<script>
  window.BODYSCAN_KB_API = 'https://seu-dominio.com/api/kb';
</script>
<script src="kb-widget.js"></script>
```

O widget lê automaticamente do `localStorage`:
- `bodyscan_peso_atual` — sincronizado ao salvar anotações
- `bodyscan_altura_cm` — configurável no widget
- `bodyscan_ca_cm` — circunferência abdominal
- `bodyscan_tipo_cirurgia` — `rygb` | `sleeve`

---

## 8. Deploy em produção (Docker)

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY kb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY kb/ .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "api.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", "--log-level", "warning"]
```

### docker-compose.yml

```yaml
version: '3.9'
services:
  db:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: bodyscan_kb
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./kb/db/schema.sql:/docker-entrypoint-initdb.d/01_schema.sql
      - ./kb/db/seed_conhecimento.sql:/docker-entrypoint-initdb.d/02_seed.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@db:5432/bodyscan_kb
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_EMBED_MODEL: text-embedding-3-small
      OPENAI_CHAT_MODEL: gpt-4o-mini
      API_ENV: production
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
```

```bash
# Deploy
docker-compose up -d

# Ingestão inicial
docker-compose exec api python3 scripts/run_ingestao.py
```

---

## 9. Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/v1/recomendacoes` | Recomendação com governança clínica |
| `GET` | `/v1/conhecimento/buscar` | Busca semântica na KB |
| `POST` | `/v1/ingestao/documento` | Ingerir novo documento |
| `POST` | `/v1/feedback` | Registrar feedback do usuário |
| `GET` | `/v1/metricas` | Métricas de observabilidade |
| `GET` | `/v1/lgpd/{id}/dados` | Exportar dados do titular (Art. 18 II) |
| `POST` | `/v1/lgpd/{id}/revogar` | Revogar consentimento (Art. 18 IV/VI) |
| `GET` | `/v1/lgpd/{id}/status` | Status de consentimento (Art. 18 I) |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Documentação interativa (Swagger UI) |

### Exemplo: Recomendação

```bash
curl -X POST http://localhost:8000/v1/recomendacoes \
  -H "Content-Type: application/json" \
  -d '{
    "pseudonimo": "usuario_anonimo_001",
    "pergunta": "Como preservar massa muscular durante a perda de peso?",
    "metricas": [
      {"biomarcador": "peso", "valor": 95.0},
      {"biomarcador": "imc", "valor": 31.2}
    ],
    "contexto_clinico": "perda_acelerada",
    "incluir_supervisao": false,
    "k": 6
  }'
```

---

## 10. Observabilidade

Todos os logs são estruturados e incluem:
- `request_id` — ID único por requisição (também no header `X-Request-ID`)
- `latency_ms` — Latência em milissegundos (também no header `X-Latency-Ms`)
- `method`, `path`, `status` — Dados HTTP

```bash
# Filtrar logs de escalonamento
journalctl -u bodyscan-kb | grep "escalonamento=True"

# Verificar métricas
curl http://localhost:8000/v1/metricas | jq .
```

---

## 11. Conformidade LGPD

O sistema implementa os direitos do titular (Art. 18, Lei 13.709/2018):

```bash
# Exportar dados do titular
curl http://localhost:8000/v1/lgpd/meu_pseudonimo/dados

# Revogar consentimento (anonimiza e remove métricas)
curl -X POST http://localhost:8000/v1/lgpd/meu_pseudonimo/revogar

# Verificar status
curl http://localhost:8000/v1/lgpd/meu_pseudonimo/status
```

**Dados armazenados:** apenas pseudônimo (sem nome, CPF, e-mail ou qualquer PII direta).

---

## 12. Testes

```bash
cd kb/

# Todos os testes E2E (requer API em execução na porta 8000)
python3 -m pytest tests/test_e2e.py -v

# Testes unitários de recuperação (sem API)
python3 scripts/test_m3_recuperacao.py

# Busca vetorial
python3 scripts/test_vector_search.py
```

**Cobertura dos critérios de aceite:**

| Critério | Teste | Status |
|---|---|---|
| RF-01: vw_recomendacao_com_evidencia | `test_rf01_*` | ✓ |
| RF-02: vw_chunk_servivel | `test_rf02_*` | ✓ |
| RF-03: Sem embedding NULL | `test_rf03_*` | ✓ |
| RF-04: Recuperação com contexto | `test_rf04_*` | ✓ |
| RF-05: Camada de regras (RCA) | `test_rf05_*` | ✓ |
| RF-07: Gate de escalonamento | `test_rf07_*` | ✓ |
| RF-08: Gate de supervisão | `test_rf08_*` | ✓ |
| RF-09: log_id em toda saída | `test_rf09_*` | ✓ |
| RF-10: Feedback vinculado | `test_rf10_*` | ✓ |
| RF-12: Não-cobertura | `test_rf12_*` | ✓ |
| RNF-02: Sem PII nos logs | `test_rnf02_*` | ✓ |
| RNF-03: Consentimento LGPD | `test_rnf03_*` | ✓ |
| RNF-04: Observabilidade | `test_observabilidade_*` | ✓ |
| RNF-05: Métricas de uso | `test_metricas_*` | ✓ |

---

## 13. Notas de segurança

- **Secrets:** nunca commitar `.env`. Usar variáveis de ambiente ou secret manager.
- **CORS:** em produção, restringir `allow_origins` às origens do frontend.
- **Rate limiting:** adicionar `slowapi` ou nginx rate limiting em produção.
- **HTTPS:** obrigatório em produção (TLS via nginx/caddy).
- **Autenticação:** adicionar JWT/API Key para endpoints de ingestão e LGPD em produção.
- **Backup:** agendar `pg_dump` diário com retenção de 30 dias.
