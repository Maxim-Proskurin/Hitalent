FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install "poetry~=1.8"

# сначала метаданные для кэша
COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-interaction --no-ansi

# затем весь проект (включая alembic, app)
COPY . .

EXPOSE 8000
