from __future__ import annotations

import os

os.environ.setdefault("ENV", "local")
os.environ.setdefault("APP_NAME", "hitalent")
os.environ.setdefault("POSTGRES_USER", "postgres")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "hitalent_test")
os.environ.setdefault("POSTGRES_HOST_LOCAL", "127.0.0.1")
os.environ.setdefault("POSTGRES_PORT_LOCAL", "5432")
os.environ.setdefault("POSTGRES_HOST_DOCKER", "db")
os.environ.setdefault("POSTGRES_PORT_DOCKER", "5432")


import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db import get_session
from app.main import app
from app.models import Base


@pytest.fixture(scope="session")
def anyio_backend():
    # Позволяет использовать pytest-asyncio/anyio вместе
    return "asyncio"


@pytest.fixture(scope="session")
def event_loop():
    # Отдельный event loop на всю сессию тестов
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db_url(tmp_path_factory) -> str:
    # Файловая БД, чтобы несколько соединений видели одну и ту же схему
    db_file = tmp_path_factory.mktemp("db") / "test.sqlite3"
    return f"sqlite+aiosqlite:///{db_file}"


@pytest_asyncio.fixture(scope="session")
async def engine_test(test_db_url):
    engine = create_async_engine(test_db_url, echo=False, future=True)
    try:
        # Создаём таблицы один раз на сессию
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield engine
    finally:
        # Сносим схему по окончании всех тестов
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def session_maker(engine_test):
    return async_sessionmaker(
        bind=engine_test,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest_asyncio.fixture
async def db_session(session_maker) -> AsyncGenerator[AsyncSession, None]:
    """Живой AsyncSession для юзер-кейсов в тестах (если нужно напрямую)."""
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def override_session_dependency(session_maker):
    """
    Подмена зависим-ти get_session у приложения на тестовый Session.
    Делается AUTOUSE, чтобы действовало во всех тестах автоматически.
    """

    async def _get_session_override() -> AsyncGenerator[AsyncSession, None]:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_session] = _get_session_override
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_session, None)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Нормальный HTTP-клиент поверх ASGI-приложения.
    ВАЖНО: это не async-генератор, который возвращается наружу,
    а фикстура, которая YIELD'ит готовый AsyncClient.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
