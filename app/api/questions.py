"""Эндпоинты для «вопросов»: создать, список, получить, удалить."""

from __future__ import annotations

import logging
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.db import get_session
from app.models import Question

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/questions", tags=["Вопросы"])


@router.post("/", response_model=schemas.QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    payload: schemas.QuestionCreate, session: AsyncSession = Depends(get_session)
):
    """Создать новый вопрос."""
    q = Question(text=payload.text)
    session.add(q)
    await session.flush()
    await session.commit()
    await session.refresh(q)
    logger.info("Создан вопрос id=%s", q.id)
    return schemas.QuestionRead.model_validate(q.__dict__)


@router.get("/", response_model=list[schemas.QuestionRead])
async def list_questions(
    response: Response,
    limit: int = 20,
    offset: int = 0,
    sort_by: Literal["id", "created_at"] = "id",
    order: Literal["asc", "desc"] = "asc",
    session: AsyncSession = Depends(get_session),
):
    """Список вопросов с пагинацией и сортировкой.

    В заголовок ответа кладём общее количество (ASCII-безопасное имя).
    """
    total = (await session.execute(select(func.count(Question.id)))).scalar_one()
    response.headers["X-Total-Count"] = str(total)

    order_by_col = Question.id if sort_by == "id" else Question.created_at
    order_expr = asc(order_by_col) if order == "asc" else desc(order_by_col)

    res = await session.execute(select(Question).order_by(order_expr).limit(limit).offset(offset))
    items = res.scalars().all()
    return [schemas.QuestionRead.model_validate(i.__dict__) for i in items]


@router.get("/{question_id}", response_model=schemas.QuestionRead)
async def get_question(question_id: int, session: AsyncSession = Depends(get_session)):
    """Получить вопрос по id."""
    res = await session.execute(select(Question).where(Question.id == question_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")
    return schemas.QuestionRead.model_validate(obj.__dict__)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, session: AsyncSession = Depends(get_session)):
    """Удалить вопрос (ответы удаляются каскадом)."""
    res = await session.execute(select(Question).where(Question.id == question_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")
    await session.delete(obj)
    await session.commit()
    logger.info("Удалён вопрос id=%s", question_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
