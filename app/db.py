"""
Асинхронный движок и фабрика сессий SQLAlchemy.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import settings

# асинхронный движок SQLAlchemy.
engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

# фабрика сессий.
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Зависимость для FastAPI.
    Отдает асинхронную сессию sqlalchemy и закрывает ее после использования.
    """
    async with AsyncSessionLocal as session:
        yield session
