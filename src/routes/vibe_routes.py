from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any

from src.models.vibe_model import (
    ProfessionCard, 
    VibeGenerateResponse,
    VibeQuestionsRequest,
    VibeQuestionsResponse,
    ClarifyingQuestion,
    QuestionOption
)
from src.utils.auth import verify_token
from src.database.db import get_user_by_username
from src.database.personality_db import get_latest_personality_result
from src.database.astro_db import get_astro_profile
from src.agent.core.profession_cards_agent import ProfessionCardsAgent
from src.agent.core.profession_vibe_agent import ProfessionVibeAgent

router = APIRouter(prefix="/vibe", tags=["Vibe Generator"])
security = HTTPBearer()


@router.post("/generate", response_model=VibeGenerateResponse)
async def generate_profession_cards(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Генерация персонализированных карточек профессий на основе теста личности и астрологии
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
    
    # Получаем данные теста личности
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
    except Exception:
        pass  # Personality data is optional
    
    # Получаем данные астрологии
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
    except Exception:
        pass  # Astrology data is optional
    
    # Проверяем, что есть хотя бы один источник данных
    if not personality_data and not astrology_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Необходимо пройти тест личности или создать астрологический профиль"
        )
    
    # Создаем агента и генерируем карточки
    try:
        agent = ProfessionCardsAgent(
            personality_data=personality_data,
            astrology_data=astrology_data,
            temperature=0.4,
            max_tokens=8192,
        )
        
        cards_data = await agent.generate_profession_cards()
        
        # Преобразуем в модели Pydantic
        profession_cards = [
            ProfessionCard(
                id=card.get("id"),
                title=card.get("title"),
                description=card.get("description"),
                matchScore=card.get("matchScore"),
                basedOn=card.get("basedOn", []),
                icon=card.get("icon"),
                gradient=card.get("gradient"),
            )
            for card in cards_data
        ]
        
        return VibeGenerateResponse(
            professions=profession_cards,
            total_count=len(profession_cards),
            has_personality_data=personality_data is not None,
            has_astrology_data=astrology_data is not None,
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка генерации карточек: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post("/questions", response_model=VibeQuestionsResponse)
async def get_profession_questions(
    request: VibeQuestionsRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Получение уточняющих вопросов о выбранной профессии
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
                "strengths": personality_result.get("strengths"),
                "weaknesses": personality_result.get("weaknesses"),
            }
    except Exception:
        pass
    
    # Получаем данные астрологии (опционально)
    astrology_data = None
    try:
        astro_profile = get_astro_profile(user["id"])
        if astro_profile:
            astrology_data = {
                "zodiac_sign": astro_profile.get("zodiac_sign"),
                "element": astro_profile.get("element"),
                "traits": astro_profile.get("traits"),
                "strengths": astro_profile.get("strengths"),
            }
    except Exception:
        pass
    
    # Создаем агента и генерируем вопросы
    try:
        agent = ProfessionVibeAgent(
            profession_title=request.profession_title,
            personality_data=personality_data,
            astrology_data=astrology_data,
            temperature=0.5,
            max_tokens=4096,
        )
        
        questions_data = await agent.generate_questions()
        
        # Преобразуем в модели Pydantic
        questions = [
            ClarifyingQuestion(
                id=q.get("id"),
                question=q.get("question"),
                allow_custom_answer=q.get("allow_custom_answer", True),
                options=[
                    QuestionOption(
                        id=opt.get("id"),
                        text=opt.get("text")
                    )
                    for opt in q.get("options", [])
                ]
            )
            for q in questions_data.get("questions", [])
        ]
        
        return VibeQuestionsResponse(questions=questions)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка генерации вопросов: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

