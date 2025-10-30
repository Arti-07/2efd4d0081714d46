from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


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
    type: str = Field(..., description="Тип: course, book, video, documentation, community, certification")
    title: str = Field(..., description="Название ресурса")
    description: str = Field(..., description="Почему ресурс ценен")
    link: Optional[str] = Field(None, description="URL ресурса")


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
    tips: List[str] = Field(..., description="Персонализированные советы (2-4 пункта)")


class RoadmapOverview(BaseModel):
    """Обзор roadmap"""
    description: str = Field(..., description="Краткое описание профессии и карьерного пути")
    totalDuration: str = Field(..., description="Общая длительность до уровня эксперта")
    keySkills: List[str] = Field(..., description="Ключевые навыки (5-7 пунктов)")
    personalityInsight: Optional[str] = Field(None, description="Как личность соответствует профессии")
    astrologyInsight: Optional[str] = Field(None, description="Астрологическая перспектива")


class RoadmapMilestone(BaseModel):
    """Важная веха в карьерном развитии"""
    id: str = Field(..., description="Идентификатор вехи")
    title: str = Field(..., description="Название вехи")
    stage: str = Field(..., description="На каком этапе достигается")
    description: str = Field(..., description="Что означает достижение вехи")
    criteria: List[str] = Field(..., description="Критерии успеха")


class RoadmapCertification(BaseModel):
    """Сертификация"""
    name: str = Field(..., description="Название сертификации")
    provider: str = Field(..., description="Организация-провайдер")
    stage: str = Field(..., description="На каком этапе рекомендуется")
    description: str = Field(..., description="Ценность сертификации")
    optional: bool = Field(..., description="Является ли опциональной")


class RoadmapCareerPath(BaseModel):
    """Возможное направление специализации"""
    title: str = Field(..., description="Название направления")
    description: str = Field(..., description="Что включает это направление")
    fromStage: str = Field(..., description="С какого этапа доступно")
    skills: List[str] = Field(..., description="Необходимые навыки")


class ProfessionRoadmap(BaseModel):
    """Полный roadmap по профессии"""
    profession: str = Field(..., description="Название профессии")
    overview: RoadmapOverview = Field(..., description="Обзор roadmap")
    stages: List[RoadmapStage] = Field(..., description="Этапы развития (5 этапов)")
    milestones: List[RoadmapMilestone] = Field(..., description="Ключевые вехи (8-15)")
    certifications: List[RoadmapCertification] = Field(..., description="Сертификации (3-8)")
    careerPaths: List[RoadmapCareerPath] = Field(..., description="Направления специализации (3-5)")


class RoadmapGenerateRequest(BaseModel):
    """Запрос на генерацию roadmap"""
    profession_title: str = Field(..., description="Название профессии")
    current_level: Optional[str] = Field(None, description="Текущий уровень пользователя")


class RoadmapGenerateResponse(BaseModel):
    """Ответ с сгенерированным roadmap"""
    roadmap: ProfessionRoadmap = Field(..., description="Сгенерированный roadmap")
    has_personality_data: bool = Field(..., description="Использовались ли данные личности")
    has_astrology_data: bool = Field(..., description="Использовались ли астрологические данные")

