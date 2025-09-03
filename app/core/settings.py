"""
Настройки приложения.
Все секреты ТОЛЬКО из переменных окружения.
Поддерживаются два режима:
- ENV=local  - локальный запуск, берём HOST/PORT из *_LOCAL
- ENV=docker - запуск в контейнере, берём HOST/PORT из *_DOCKER
"""

from __future__ import annotations

from urllib.parse import quote

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic Settings для приложения.

    Обязательные переменные окружения:
      - POSTGRES_USER
      - POSTGRES_PASSWORD
      - POSTGRES_DB

    Режимы и адреса:
      - ENV = local | docker (по умолчанию: local)
      - POSTGRES_HOST_LOCAL, POSTGRES_PORT_LOCAL
      - POSTGRES_HOST_DOCKER, POSTGRES_PORT_DOCKER
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # базовое
    env: str = "local"  # local | docker
    app_name: str = "hitalent"

    # postgres (обязательные)
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # postgres (варианты хоста/порта)
    postgres_host_local: str | None = None
    postgres_port_local: int | None = None
    postgres_host_docker: str | None = None
    postgres_port_docker: int | None = None

    # тюнинг пулов (опционально)
    sql_echo: bool = False
    sql_pool_size: int = 5
    sql_max_overflow: int = 10
    sql_pool_pre_ping: bool = True

    @property
    def postgres_host(self) -> str:
        """Хост для Postgres в зависимости от режима."""
        if self.env == "docker":
            return self.postgres_host_docker or "db"
        return self.postgres_host_local or "127.0.0.1"

    @property
    def postgres_port(self) -> int:
        """Порт для Postgres в зависимости от режима."""
        if self.env == "docker":
            return int(self.postgres_port_docker or 5432)
        return int(self.postgres_port_local or 5432)

    @staticmethod
    def _q(s: str) -> str:
        """Экранирует спецсимволы в логине/пароле для DSN."""
        return quote(s, safe="")

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Синхронный DSN (для Alembic)."""
        return (
            "postgresql+psycopg://"
            f"{self._q(self.postgres_user)}:{self._q(self.postgres_password)}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """Асинхронный DSN (для приложения)."""
        return (
            "postgresql+asyncpg://"
            f"{self._q(self.postgres_user)}:{self._q(self.postgres_password)}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # совместимость с нижним регистром
    @property
    def database_url_sync(self) -> str:
        return self.DATABASE_URL_SYNC

    @property
    def database_url_async(self) -> str:
        return self.DATABASE_URL_ASYNC


settings = Settings()
