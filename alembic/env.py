# isort: skip_file
"""
Alembic использует настройки из .env (через Settings) и применяет миграции.
"""
import asyncio
import sys
from logging.config import fileConfig

from alembic import context  # type: ignore[attr-defined]
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine, async_engine_from_config

from app.core.settings import settings
from app.models import Base

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в offline-режиме."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Общий блок конфигурации context для online-режима."""
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Запуск миграций в online-режиме."""
    connectable: AsyncEngine = async_engine_from_config(
        {"sqlalchemy.url": settings.DATABASE_URL},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def is_revision_command() -> bool:
    """Определяю, что запущена команда 'revision' (есть флаг autogenerate)."""
    cmd_opts = getattr(config, "cmd_opts", None)
    return bool(cmd_opts and getattr(cmd_opts, "autogenerate", False))

if is_revision_command():
    run_migrations_offline()
    sys.exit(0)

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
