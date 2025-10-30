from pydantic import BaseModel, Field
from typing import List, Optional


class RoadmapSkill(BaseModel):
    """Модель навыка в roadmap"""
    name: str = Field(..., description="Название навыка")
    description: str = Field(..., description="Описание навыка")
    importance: str = Field(..., description="Важность: high, medium, low")


class RoadmapTool(BaseModel):
    """Модель инструмента/технологии в roadmap"""
    name: str = Field(..., description="Название инструмента")
    category: str = Field(..., description="Категория: framework, language, platform, software, tool")
    description: str = Field(..., description="Описание инструмента")


class RoadmapProject(BaseModel):
    """Модель проекта для практики"""
    title: str = Field(..., description="Название проекта")
    description: str = Field(..., description="Что нужно построить и зачем")
    skills: List[str] = Field(..., description="Навыки, которые применяются")


class RoadmapResource(BaseModel):
    """Модель ресурса для обучения"""
    type: str = Field(..., description="Тип: course, book, video, documentation, community")
    title: str = Field(..., description="Название ресурса")
    description: str = Field(..., description="Почему ресурс ценен")
    link: Optional[str] = Field(None, description="URL ресурса")


class InterviewQuestion(BaseModel):
    """Модель вопроса на собеседовании"""
    question: str = Field(..., description="Вопрос на собеседовании")
    answer: str = Field(..., description="Ответ на вопрос")


class RoadmapStage(BaseModel):
    """Модель этапа карьерного развития"""
    id: str = Field(..., description="Идентификатор этапа")
    level: str = Field(..., description="Уровень: BEGINNER, JUNIOR, MIDDLE, SENIOR, EXPERT")
    title: str = Field(..., description="Название этапа")
    duration: str = Field(..., description="Длительность этапа")
    description: str = Field(..., description="Описание этапа")
    goals: List[str] = Field(..., description="Цели этапа (3-5 пунктов)")
    skills: List[RoadmapSkill] = Field(..., description="Навыки для изучения (3-7 пунктов)")
    tools: List[RoadmapTool] = Field(..., description="Инструменты для освоения (3-10 пунктов)")
    projects: List[RoadmapProject] = Field(..., description="Проекты для практики (2-4 пункта)")
    resources: List[RoadmapResource] = Field(..., description="Ресурсы для обучения (3-6 пунктов)")
    interviewQuestions: List[InterviewQuestion] = Field(default_factory=list, description="Вопросы на собеседовании (5-10 пунктов)")
    
    class Config:
        # Разрешаем дополнительные поля (для обратной совместимости)
        extra = "allow"


class RoadmapOverview(BaseModel):
    """Обзор roadmap"""
    description: str = Field(..., description="Краткое описание профессии и карьерного пути")
    totalDuration: str = Field(..., description="Общая длительность до уровня эксперта")
    keySkills: List[str] = Field(..., description="Ключевые навыки (5-7 пунктов)")
    personalityInsight: Optional[str] = Field(None, description="Как личность соответствует профессии")
    astrologyInsight: Optional[str] = Field(None, description="Астрологическая перспектива")


class ProfessionRoadmap(BaseModel):
    """Полный roadmap по профессии"""
    profession: str = Field(..., description="Название профессии")
    overview: RoadmapOverview = Field(..., description="Обзор roadmap")
    stages: List[RoadmapStage] = Field(..., description="Этапы развития (5 этапов)")
    
    class Config:
        # Убеждаемся что все поля сериализуются
        validate_assignment = True


class RoadmapGenerateRequest(BaseModel):
    """Запрос на генерацию roadmap"""
    profession_title: str = Field(..., description="Название профессии")
    current_level: Optional[str] = Field(None, description="Текущий уровень пользователя")


class RoadmapGenerateResponse(BaseModel):
    """Ответ с сгенерированным roadmap"""
    roadmap: ProfessionRoadmap = Field(..., description="Сгенерированный roadmap")
    has_personality_data: bool = Field(..., description="Использовались ли данные личности")
    has_astrology_data: bool = Field(..., description="Использовались ли астрологические данные")
