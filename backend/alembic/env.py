from __future__ import annotations

from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool

# 0) Tornar o pacote "app" importável quando o Alembic roda a partir de alembic/
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[1]  # pasta que contém app/ e alembic/
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# 1) Imports do seu projeto (depois do sys.path)
from app.core.settings import get_settings
from app.models.base import Base
import app.models  # <-- importa o pacote que auto-carrega todos os models

# 2) Config padrão do Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
settings = get_settings()

def run_migrations_offline() -> None:
    """Gera SQL sem abrir conexão."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Aplica migrações com conexão."""
    configuration = config.get_section(config.config_ini_section) or {}
    # >>> AQUI É O PULO DO GATO: injetar a URL do Settings <<<
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
