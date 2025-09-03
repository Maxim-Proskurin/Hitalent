"""
Pydantic-схемы и минимальные проверки данных на входе/выходе.
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuestionBase(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """Не допускаем пустой текст вопроса."""
        if not v or not v.strip():
            raise ValueError("Текст не должен быть пустым")
        return v.strip()


class QuestionCreate(QuestionBase):
    """Схема для создания вопроса."""

    pass


class QuestionRead(QuestionBase):
    """Схема для ответа API (вопрос)."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnswerBase(BaseModel):
    user_id: UUID
    text: str

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        """Не допустить пустой текст ответа."""
        if not v or not v.strip():
            raise ValueError("Текст не должен быть пустым")
        return v.strip()


class AnswerCreate(AnswerBase):
    """Схема для создания ответа."""

    pass


class AnswerRead(AnswerBase):
    """Схема для ответа API (ответ)."""

    id: int
    question_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionWithAnswers(QuestionRead):
    """Вопрос вместе со списком ответов."""

    answers: List[AnswerRead] = Field(default_factory=list)
