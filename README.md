# Этот проект - решение тестового задания на позицию Junior Python разработчика в компанию Хайталент. Задача: реализовать сервис «Вопросы / Ответы» с использованием FastAPI + PostgreSQL + Alembic + Docker, покрыть тестами и подготовить документацию

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![Poetry](https://img.shields.io/badge/poetry-2.1.3-60A5FA.svg)
![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![Black](https://img.shields.io/badge/code%20style-black-000000.svg)
![isort](https://img.shields.io/badge/imports-isort-ef8336.svg)
![Ruff](https://img.shields.io/badge/linter-ruff-ff2b2b.svg)
![mypy](https://img.shields.io/badge/types-mypy-2A6DB3.svg)
[![CI](https://github.com/Maxim-Proskurin/Hitalent/actions/workflows/ci.yml/badge.svg)](https://github.com/Maxim-Proskurin/Hitalent/actions/workflows/ci.yml)

## Реализовано

- CRUD для вопросов и ответов.
- Асинхронный стек (fastapi, sqlalchemy[asyncio], asyncpg).
- Миграции через Alembic.
- Логи старта и ключевых действий.
- Поддержка работы и в Docker, и локально.
- Автотесты с покрытием.

### Технологии

- Python 3.12.
- FastAPI.
- SQLAlchemy 2.x (async) + asyncpg.
- Alembic.
- Pydantic v2 / pydantic-settings.
- Poetry.
- Docker Compose.
- pytest + pytest-asyncio + httpx.

### Структура

app/

- api/              # эндпоинты (questions, answers)
- core/             # конфиги (logging, settings)
- db.py             # подключение к БД
- main.py           # FastAPI-приложение
- models.py         # SQLAlchemy модели
- schemas.py        # Pydantic-схемы
- alembic/            # миграции
- tests/              # тесты + фикстуры
- docker-compose.yml  # запуск в контейнерах
- Dockerfile
- pyproject.toml
- .env.example        # пример заполнения env

### Запуск

В Docker.

``` bash
docker compose up -d --build
docker compose run --rm app alembic upgrade head
```

Локально.

``` bash
poetry install
docker compose up -d db
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

### Тесты и покрытие

``` bash
poetry run pytest --cov=app --cov-report=term-missing
```

### Основные эндпоинты

Вопросы.

- POST /questions/ - создать вопрос.
- GET /questions/ - список (пагинация + сортировка).
- GET /questions/{id} - получить по ID.
- DELETE /questions/{id} - удалить.

Ответы.

- POST /answers/questions/{question_id}/ - создать ответ на вопрос.
- GET /answers/ - список (фильтр по question_id).
- GET /answers/{id} - получить ответ.
- DELETE /answers/{id} - удалить.

### Миграции

Создать новую миграцию.

``` bash
poetry run alembic revision --autogenerate -m "описание"
```

Применить.

```bash
poetry run alembic upgrade head
```

### Линтинг и автоформат

- black - автоформатирование.
- isort - сортировка импортов.
- ruff - линтинг (заменяет flake8 + pylint).
- mypy - статическая проверка типов.

Установка.

```bash
poetry run pre-commit install
```

Запуск вручную.

```bash
poetry run pre-commit install
```

### CI/CD(Github Actions)

В репозитории настроен CI-пайплайн:
каждый push и pull request автоматически запускает:

- Установка зависимостей через Poetry.
- Линтинг (ruff, black, isort, mypy).
- Тесты с покрытием (pytest --cov).
- Отчёт о покрытии в консоль.

### Итог

- Работает как локально, так и в Docker(главное что бы база была поднята.)
- Есть тесты с покрытием.
- Четкая структура проекта.
- Подробный README для запуска.
- Миграции.
- Линтинг + типы.
- CI-pipeline.

**Автор**
Максим Проскурин

**Способы Связи**
[![💬 Написать в Telegram](https://img.shields.io/badge/💬-Telegram-26A5E4?style=flat&logo=telegram&logoColor=white)](https://t.me/woolwerine)
[![📧 Написать письмо](https://img.shields.io/badge/📧_Написать-D14836?style=flat&logo=gmail&logoColor=white)](https://mail.yandex.ru/compose?mailto=Maxiprsk@yandex.ru)
