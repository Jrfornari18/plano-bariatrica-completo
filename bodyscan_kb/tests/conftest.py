"""
conftest.py — Fixtures compartilhadas para testes do BodyScan KB.

Usa asyncpg diretamente (sem SQLAlchemy) com PostgreSQL de desenvolvimento.
"""
import os

# Garante que o provedor de embeddings seja local durante os testes
os.environ.setdefault("EMBED_PROVIDER", "local")

# Ignora diretórios de testes de outros módulos que usam SQLAlchemy/SQLite
collect_ignore_glob = ["unit/*", "integration/*"]
