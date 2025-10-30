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
    allow_custom_answer: bool = Field(default=True, description="Разрешить пользователю ввести свой ответ")
    options: List[QuestionOption] = Field(..., description="Варианты ответа")


class VibeQuestionsRequest(BaseModel):
    """Запрос на получение уточняющих вопросов"""
    profession_title: str = Field(..., description="Название профессии")


class VibeQuestionsResponse(BaseModel):
    """Ответ с уточняющими вопросами"""
    questions: List[ClarifyingQuestion] = Field(..., description="Список вопросов")


class ProfessionValidateRequest(BaseModel):
    """Запрос на валидацию профессии"""
    profession_title: str = Field(..., description="Название профессии для проверки")


class ProfessionValidateResponse(BaseModel):
    """Ответ с результатом валидации профессии"""
    is_valid: bool = Field(..., description="Является ли профессия валидной")
    status: str = Field(..., description="Статус: valid, invalid, too_general, rare, obsolete")
    message: str = Field(..., description="Сообщение для пользователя")
    suggestions: List[str] = Field(default=[], description="Предложенные альтернативы")
    found_count: int = Field(..., description="Количество найденных вакансий")
    sample_vacancies: List[str] = Field(default=[], description="Примеры названий вакансий")
    hh_total_found: int = Field(..., description="Общее количество на HH.ru")
    query: str = Field(..., description="Исходный запрос")


class AmbientEnvironment(BaseModel):
    """Модель одного окружения (амбиента) профессии"""
    id: str = Field(..., description="Идентификатор окружения")
    name: str = Field(..., description="Название окружения")
    text: str = Field(..., description="Текстовое описание ситуации")
    image_prompt: str | None = Field(default=None, description="Промпт для генерации изображения (на английском)")
    sound_prompt: str | None = Field(default=None, description="Промпт для генерации звуков")
    voice: str | None = Field(default=None, description="Текст голоса/речи в этом окружении")


class ProfessionTools(BaseModel):
    """Модель инструментов профессии"""
    title: str = Field(..., description="Заголовок секции инструментов")
    items: List[str] = Field(..., description="Список инструментов с эмодзи")


class QuestionAnswer(BaseModel):
    """Модель ответа на уточняющий вопрос"""
    question_id: str = Field(..., description="ID вопроса")
    question_text: str = Field(..., description="Текст вопроса")
    answer: str = Field(..., description="Ответ пользователя")


class AmbientsGenerateRequest(BaseModel):
    """Запрос на генерацию окружений профессии"""
    profession_title: str = Field(..., description="Название выбранной профессии")
    question_answers: List[QuestionAnswer] = Field(..., description="Ответы на уточняющие вопросы")


class AmbientsGenerateResponse(BaseModel):
    """Ответ с окружениями профессии"""
    profession_title: str = Field(..., description="Название профессии")
    ambients: List[AmbientEnvironment] = Field(..., description="Список окружений")
    tools: ProfessionTools = Field(..., description="Инструменты профессии")