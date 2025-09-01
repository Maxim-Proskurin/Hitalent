"""
Маршруты по вопросам и добавлению ответов к ним.
"""

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.models import Answer, Question
from app.schemas import AnswerCreate, AnswerRead, QuestionCreate, QuestionRead, QuestionWithAnswers

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/", response_model=List[QuestionRead])
async def list_questions(
    response: Response,
    session: AsyncSession = Depends(get_session),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: Literal["id", "created_at"] = Query("id"),
    order: Literal["asc", "desc"] = Query("asc"),
    q: Optional[str] = Query(None),
) -> List[QuestionRead]:
    """
    Вернуть список вопросов.

    - limit, offset управляют пагинацией
    - sort_by, order управляют сортировкой
    - q фильтрует по подстроке в тексте
    - заголовок X-Общее-Количество содержит общее количество записей по фильтру
    """
    # считаем общее количество по текущему фильтру
    count_stmt = select(func.count()).select_from(Question)
    if q:
        count_stmt = count_stmt.where(Question.text.contains(q))
    total = (await session.execute(count_stmt)).scalar_one()
    response.headers["X-Общее-Количество"] = str(total)

    # основная выборка
    stmt = select(Question)
    if q:
        stmt = stmt.where(Question.text.contains(q))

    order_col = getattr(Question, sort_by)
    stmt = stmt.order_by(asc(order_col) if order == "asc" else desc(order_col))
    stmt = stmt.limit(limit).offset(offset)

    result = await session.execute(stmt)
    return list(result.scalars().all)


@router.post("/", response_model=QuestionRead, status_code=status.HTTP_201_CREATED)
async def create_question(
    payload: QuestionCreate, session: AsyncSession = Depends(get_session)
) -> QuestionRead:
    """Создать новый вопрос."""
    item = Question(text=payload.text)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("/{question_id}", response_model=QuestionWithAnswers)
async def get_question(
    question_id: int, session: AsyncSession = Depends(get_session)
) -> QuestionWithAnswers:
    """Вернуть один вопрос вместе с его ответами."""
    result = await session.execute(
        select(Question).options(selectinload(Question.answers)).where(Question.id == question_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Вопрос не найден.")
    return item


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int, session: AsyncSession = Depends(get_session)) -> None:
    """Удалить вопрос. Связанные ответы удаляются каскадом."""
    item = await session.get(Question, question_id)
    if not item:
        raise HTTPException(status_code=404, detail="Вопрос не найден.")
    await session.delete(item)
    await session.commit()
    return None


@router.post(
    "/{question_id}/answers/",
    response_model=AnswerRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_answer_to_question(
    question_id: int, payload: AnswerCreate, session: AsyncSession = Depends(get_session)
) -> AnswerRead:
    """Добавить ответ к существующему вопросу. Если Вопрос не найден. - 404."""
    qobj = await session.get(Question, question_id)
    if not qobj:
        raise HTTPException(status_code=404, detail="Вопрос не найден.")

    ans = Answer(question_id=question_id, user_id=str(payload.user_id), text=payload.text)
    session.add(ans)
    await session.commit()
    await session.refresh(ans)
    return ans
