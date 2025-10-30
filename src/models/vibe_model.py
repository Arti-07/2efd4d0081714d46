from pydantic import BaseModel, Field
from typing import List


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

