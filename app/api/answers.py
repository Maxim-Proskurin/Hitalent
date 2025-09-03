"""Эндпоинты для «ответов»: список, получить, создать к вопросу, удалить."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.db import get_session
from app.models import Answer, Question

logger = logging.getLogger(__name__)


# - /answers/... (CRUD по ответам)
# - /questions/{id}/answers/ (создание ответа к вопросу)
router = APIRouter(tags=["Ответы"])


@router.get("/answers/", response_model=list[schemas.AnswerRead])
async def list_answers(
    question_id: int | None = None,
    limit: int = 20,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    """Список ответов (можно отфильтровать по question_id)."""
    stmt = select(Answer)
    if question_id is not None:
        stmt = stmt.where(Answer.question_id == question_id)
    stmt = stmt.order_by(asc(Answer.id)).limit(limit).offset(offset)

    res = await session.execute(stmt)
    items = res.scalars().all()
    return [schemas.AnswerRead.model_validate(i.__dict__) for i in items]


@router.get("/answers/{answer_id}", response_model=schemas.AnswerRead)
async def get_answer(answer_id: int, session: AsyncSession = Depends(get_session)):
    """Получить ответ по id."""
    res = await session.execute(select(Answer).where(Answer.id == answer_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ответ не найден")
    return schemas.AnswerRead.model_validate(obj.__dict__)


@router.post(
    "/questions/{question_id}/answers/",
    response_model=schemas.AnswerRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_answer_for_question(
    question_id: int,
    payload: schemas.AnswerCreate,
    session: AsyncSession = Depends(get_session),
):
    """Создать ответ к конкретному вопросу."""
    q = (
        await session.execute(select(Question).where(Question.id == question_id))
    ).scalar_one_or_none()
    if not q:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Вопрос не найден")

    ans = Answer(question_id=question_id, user_id=str(payload.user_id), text=payload.text)
    session.add(ans)
    await session.flush()
    await session.refresh(ans)
    await session.commit()

    logger.info("Создан ответ id=%s для question_id=%s", ans.id, question_id)
    return schemas.AnswerRead.model_validate(ans.__dict__)


@router.delete("/answers/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(answer_id: int, session: AsyncSession = Depends(get_session)):
    """Удалить ответ по id."""
    res = await session.execute(select(Answer).where(Answer.id == answer_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ответ не найден")
    await session.delete(obj)
    await session.commit()
    logger.info("Удалён ответ id=%s", answer_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
