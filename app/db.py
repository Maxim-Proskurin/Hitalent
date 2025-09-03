from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import settings

# === Движок SQLAlchemy ===
engine = create_async_engine(
    settings.DATABASE_URL_ASYNC,
    echo=False,
    future=True,
)

# === Фабрика асинхронных сессий ===
AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# === Dependency для FastAPI ===
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронная сессия SQLAlchemy для работы с БД.
    Используется в Depends() внутри роутов.
    """
    async with AsyncSessionLocal() as session:
        yield session
