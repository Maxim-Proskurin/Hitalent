from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.answers import router as answers_router
from app.api.questions import router as questions_router
from app.core.logging_config import configure_logging
from app.core.settings import settings

# Настраиваем базовое логирование
configure_logging()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Жизненный цикл приложения:
    - при старте - пишем, с чем запустились (ENV/хост/порт/БД);
    - при остановке - аккуратно завершаемся.
    """
    logger.info(
        "ENV=%s HOST=%s PORT=%s DB=%s",
        settings.env,
        settings.postgres_host,
        settings.postgres_port,
        settings.postgres_db,
    )
    logger.info("🚀 Приложение запущено")
    yield
    logger.info("👋 Приложение остановлено")


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(questions_router)
app.include_router(answers_router)


@app.get("/", tags=["health"])
async def root():
    """healthcheck/приветствие."""
    return JSONResponse({"status": "ok", "app": settings.app_name})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
