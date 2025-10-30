from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from src.models.roadmap_model import (
    RoadmapGenerateRequest,
    RoadmapGenerateResponse,
    ProfessionRoadmap,
)
from src.utils.auth import verify_token
from src.database.db import get_user_by_username
from src.database.personality_db import get_latest_personality_result
from src.database.astro_db import get_astro_profile
from src.agent.core.profession_roadmap_agent import ProfessionRoadmapAgent

router = APIRouter(prefix="/roadmap", tags=["Career Roadmap"])
security = HTTPBearer()

logger = logging.getLogger(__name__)


@router.post("/generate", response_model=RoadmapGenerateResponse, response_model_exclude_none=False)
async def generate_profession_roadmap(
    request: RoadmapGenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Генерация карьерного roadmap для выбранной профессии
    
    Создает подробный план развития карьеры с этапами от начинающего до эксперта,
    включая навыки, инструменты, проекты, ресурсы и персонализированные советы
    на основе данных личности и астрологии пользователя.
    """
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    # Получаем данные теста личности (опционально)
    personality_data = None
    try:
        personality_result = get_latest_personality_result(user["id"])
        if personality_result:
            personality_data = {
                "code": personality_result.get("code"),
                "personality_type": personality_result.get("personality_type"),
                "description": personality_result.get("description"),
                "full_description": personality_result.get("full_description"),
                "strengths": personality_result.get("strengths"),
                "weaknesses": personality_result.get("weaknesses"),
                "career_advice": personality_result.get("career_advice"),
                "careers": personality_result.get("careers"),
            }
            logger.info(f"Retrieved personality data for user {username}: {personality_result.get('code')}")
    except Exception as e:
        logger.warning(f"Could not retrieve personality data: {str(e)}")
        pass  # Personality data is optional
    
    # Получаем данные астрологии (опционально)
    astrology_data = None
    try:
        astro_profile = get_astro_profile(user["id"])
        if astro_profile:
            astrology_data = {
                "zodiac_sign": astro_profile.get("zodiac_sign"),
                "element": astro_profile.get("element"),
                "quality": astro_profile.get("quality"),
                "traits": astro_profile.get("traits"),
                "careers": astro_profile.get("careers"),
                "strengths": astro_profile.get("strengths"),
                "challenges": astro_profile.get("challenges"),
            }
            logger.info(f"Retrieved astrology data for user {username}: {astro_profile.get('zodiac_sign')}")
    except Exception as e:
        logger.warning(f"Could not retrieve astrology data: {str(e)}")
        pass  # Astrology data is optional
    
    # Создаем агента и генерируем roadmap
    try:
        logger.info(f"Generating roadmap for profession: {request.profession_title}")
        
        agent = ProfessionRoadmapAgent(
            profession_title=request.profession_title,
            personality_data=personality_data,
            astrology_data=astrology_data,
            current_level=request.current_level,
            temperature=0.4,
            max_tokens=16384,
        )
        
        roadmap_data = await agent.generate_roadmap()
        
        # Логируем первый этап для проверки
        if roadmap_data.get('stages') and len(roadmap_data['stages']) > 0:
            first_stage = roadmap_data['stages'][0]
            logger.info(f"First stage has interviewQuestions: {'interviewQuestions' in first_stage}")
            if 'interviewQuestions' in first_stage:
                logger.info(f"Number of questions: {len(first_stage['interviewQuestions'])}")
        
        # Преобразуем в модель Pydantic для валидации
        roadmap = ProfessionRoadmap(**roadmap_data)
        
        # Проверяем после валидации
        if roadmap.stages and len(roadmap.stages) > 0:
            logger.info(f"After Pydantic: first stage has {len(roadmap.stages[0].interviewQuestions)} questions")
        
        logger.info(f"Successfully generated roadmap with {len(roadmap.stages)} stages")
        
        return RoadmapGenerateResponse(
            roadmap=roadmap,
            has_personality_data=personality_data is not None,
            has_astrology_data=astrology_data is not None,
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации roadmap: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера при генерации roadmap: {str(e)}"
        )


@router.get("/health")
async def roadmap_health_check():
    """
    Проверка доступности сервиса roadmap
    """
    return {
        "status": "healthy",
        "service": "roadmap",
        "message": "Career Roadmap Generator is operational"
    }

