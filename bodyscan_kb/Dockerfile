# BodyScan KB & Memory — Dockerfile
# Build: docker build -t bodyscan-kb .
# Run:   docker run -p 8000:8000 --env-file .env bodyscan-kb

FROM python:3.11-slim

# Metadados
LABEL maintainer="Barifit.pro"
LABEL description="BodyScan KB & Memory — Módulo de Conhecimento e Memória"

# Variáveis de build
ARG APP_DIR=/app

# Configurações de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR ${APP_DIR}

# Instalar dependências Python (camada cacheável)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte
COPY . .

# Criar diretório para banco SQLite (MVP)
RUN mkdir -p /data

# Usuário não-root por segurança
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser ${APP_DIR} /data
USER appuser

# Porta exposta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
