from pydantic import BaseModel, Field
from typing import List, Dict, Any


class ProfessionCard(BaseModel):
    """Модель карточки профессии"""
    id: str = Field(..., description="Уникальный идентификатор карточки")
    title: str = Field(..., description="Название профессии")
    description: str = Field(..., description="Описание профессии")
    matchScore: int = Field(..., ge=0, le=100, description="Процент совпадения (0-100)")
    basedOn: List[str] = Field(..., description="На чем основан анализ (Личность/Астрология)")
    icon: str = Field(..., description="Эмодзи иконка профессии")
    gradient: str = Field(..., description="CSS градиент для карточки")


class VibeGenerateResponse(BaseModel):
    """Ответ с сгенерированными карточками профессий"""
    professions: List[ProfessionCard] = Field(..., description="Список карточек профессий")
    total_count: int = Field(..., description="Общее количество карточек")
    has_personality_data: bool = Field(..., description="Наличие данных теста личности")
    has_astrology_data: bool = Field(..., description="Наличие астрологических данных")


class QuestionOption(BaseModel):
    """Вариант ответа на вопрос"""
    id: str = Field(..., description="Идентификатор варианта")
    text: str = Field(..., description="Текст варианта ответа")


class ClarifyingQuestion(BaseModel):
    """Уточняющий вопрос о профессии"""
    id: str = Field(..., description="Идентификатор вопроса")
    question: str = Field(..., description="Текст вопроса")
    options: List[QuestionOption] = Field(..., description="Варианты ответа")


class VibeQuestionsRequest(BaseModel):
    """Запрос на получение уточняющих вопросов"""
    profession_title: str = Field(..., description="Название профессии")


class VibeQuestionsResponse(BaseModel):
    """Ответ с уточняющими вопросами"""
    questions: List[ClarifyingQuestion] = Field(..., description="Список вопросов")

