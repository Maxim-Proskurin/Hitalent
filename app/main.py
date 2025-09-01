"""
Точка входа FastAPI.
"""

from fastapi import FastAPI

from app.api.answers import router as answers_router
from app.api.questions import router as questions_router
from app.core.logging_config import configure_logging
from app.core.settings import settings

configure_logging()
app = FastAPI(title=settings.app_name)

app.include_router(questions_router)
app.include_router(answers_router)


@app.get("/", tags=["health"])
def health():
    """Простой health-check."""
    return {"okay?": "lets go!"}
