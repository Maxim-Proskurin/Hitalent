"""
Маршруты по ответам: получить один, удалить один.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Answer
from app.schemas import AnswerRead

router = APIRouter(prefix="/answers", tags=["answers"])


@router.get("/{answer_id}", response_model=AnswerRead)
async def get_answer(answer_id: int, session: AsyncSession = Depends(get_session)) -> AnswerRead:
    item = await session.get(Answer, answer_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ответ не найден.")
    return item


@router.delete("/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(answer_id: int, session: AsyncSession = Depends(get_session)) -> None:
    item = await session.get(Answer, answer_id)
    if not item:
        raise HTTPException(status_code=404, detail="Ответ не найден.")
    await session.delete(item)
    await session.commit()
    return None
