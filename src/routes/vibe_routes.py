from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
import json
import base64
from pathlib import Path
from datetime import datetime
import requests
import logging

from src.models.vibe_model import (
    ProfessionCard, 
    VibeGenerateResponse,
    VibeQuestionsRequest,
    VibeQuestionsResponse,
    ClarifyingQuestion,
    QuestionOption,
    ProfessionValidateRequest,
    ProfessionValidateResponse,
    AmbientsGenerateRequest,
    AmbientsGenerateResponse,
    AmbientEnvironment,
    ProfessionTools,
    AmbientsWithMediaRequest,
    AmbientsWithMediaResponse,
    AmbientEnvironmentWithMedia,
    GenerateMediaForAmbientRequest,
    GenerateMediaForAmbientResponse
)
from src.utils.auth import verify_token
from src.database.db import get_user_by_username
from src.database.personality_db import get_latest_personality_result
from src.database.astro_db import get_astro_profile
from src.agent.core.profession_cards_agent import ProfessionCardsAgent
from src.agent.core.profession_vibe_agent import ProfessionVibeAgent
from src.agent.core.profession_validator_agent import ProfessionValidatorAgent
from src.agent.core.profession_ambients_agent import ProfessionAmbientsAgent
from src.utils.fusion_brain import FusionBrainAPI
from src.config import settings

router = APIRouter(prefix="/vibe", tags=["Vibe Generator"])
security = HTTPBearer()

logger = logging.getLogger(__name__)

# Директории для хранения медиа файлов
DATA_DIR = Path("data")
AMBIENTS_DIR = DATA_DIR / "ambients"
IMAGES_DIR = AMBIENTS_DIR / "images"
SOUNDS_DIR = AMBIENTS_DIR / "sounds"
VOICES_DIR = AMBIENTS_DIR / "voices"
JSON_DIR = AMBIENTS_DIR / "results"

# Относительные пути к шаблонным файлам (для API ответов)
# Шаблоны лежат в тех же директориях что и обычные файлы
TEMPLATE_IMAGE_PATH = "ambients/images/template_image.jpg"
TEMPLATE_SOUND_PATH = "ambients/sounds/template_sound.mp3"
TEMPLATE_VOICE_PATH = "ambients/voices/template_voice.mp3"

# Создаем директории
for directory in [IMAGES_DIR, SOUNDS_DIR, VOICES_DIR, JSON_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


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


@router.post("/validate", response_model=ProfessionValidateResponse)
async def validate_profession(
    request: ProfessionValidateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Валидация профессии через API HH.ru и AI анализ
    """
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверяем, что название профессии не пустое
    if not request.profession_title or len(request.profession_title.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Название профессии должно содержать хотя бы 2 символа"
        )
    
    # Создаем агента валидации
    try:
        agent = ProfessionValidatorAgent(
            profession_title=request.profession_title,
            temperature=0.3,
            max_tokens=2048,
        )
        
        validation_result = await agent.validate_profession()
        
        return ProfessionValidateResponse(
            is_valid=validation_result.get("is_valid", False),
            status=validation_result.get("status", "unknown"),
            message=validation_result.get("message", ""),
            suggestions=validation_result.get("suggestions", []),
            found_count=validation_result.get("found_count", 0),
            sample_vacancies=validation_result.get("sample_vacancies", []),
            hh_total_found=validation_result.get("hh_total_found", 0),
            query=validation_result.get("query", request.profession_title),
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка валидации: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post("/ambients", response_model=AmbientsGenerateResponse)
async def generate_profession_ambients(
    request: AmbientsGenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Генерация окружений (амбиентов) для выбранной профессии
    на основе всех собранных данных: личность, астрология, профессия, уточняющие вопросы
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
    
    # Формируем данные уточняющих вопросов
    clarifying_data = {
        "questions": [
            {
                "id": qa.question_id,
                "question": qa.question_text,
                "answer": qa.answer
            }
            for qa in request.question_answers
        ]
    }
    
    # Создаем агента и генерируем окружения
    try:
        agent = ProfessionAmbientsAgent(
            profession_title=request.profession_title,
            personality_data=personality_data,
            astrology_data=astrology_data,
            clarifying_data=clarifying_data,
            temperature=0.6,
            max_tokens=8192,
        )
        
        ambients_data = await agent.generate_ambients()
        
        # Преобразуем в модели Pydantic
        ambients = [
            AmbientEnvironment(
                id=amb.get("id"),
                name=amb.get("name"),
                text=amb.get("text"),
                image_prompt=amb.get("image_prompt"),
                sound_prompt=amb.get("sound_prompt"),
                voice=amb.get("voice"),
            )
            for amb in ambients_data.get("ambients", [])
        ]
        
        tools = ProfessionTools(
            title=ambients_data.get("tools", {}).get("title", "Инструменты профессии"),
            items=ambients_data.get("tools", {}).get("items", [])
        )
        
        return AmbientsGenerateResponse(
            profession_title=ambients_data.get("profession_title", request.profession_title),
            ambients=ambients,
            tools=tools
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка генерации окружений: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post("/ambients-with-media", response_model=AmbientsWithMediaResponse)
async def generate_profession_ambients_with_media(
    request: AmbientsWithMediaRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Генерация окружений (амбиентов) для выбранной профессии с медиа файлами
    (изображения, звуки, голоса) на основе всех собранных данных
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
    
    # Статистика генерации
    stats = {
        "images_generated": 0,
        "images_failed": 0,
        "sounds_generated": 0,
        "sounds_failed": 0,
        "voices_generated": 0,
        "voices_failed": 0,
    }
    
    try:
        # Генерируем окружения через агента
        if not request.use_template:
            # Получаем данные пользователя
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
                pass
            
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
                pass
            
            clarifying_data = {
                "questions": [
                    {
                        "id": qa.question_id,
                        "question": qa.question_text,
                        "answer": qa.answer
                    }
                    for qa in request.question_answers
                ]
            }
            
            # Создаем агента и генерируем окружения
            agent = ProfessionAmbientsAgent(
                profession_title=request.profession_title,
                personality_data=personality_data,
                astrology_data=astrology_data,
                clarifying_data=clarifying_data,
                temperature=0.6,
                max_tokens=8192,
            )
            
            ambients_data = await agent.generate_ambients()
        else:
            # Используем шаблонные данные для тестирования
            ambients_data = _get_template_ambients_data(request.profession_title)
        
        # Создаем уникальный ID для этой генерации
        generation_id = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Сохраняем исходный JSON
        json_filename = f"ambients_{generation_id}.json"
        json_path = JSON_DIR / json_filename
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(ambients_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved ambients JSON to {json_path}")
        
        # Генерируем медиа для каждого окружения
        ambients_with_media = []
        
        for i, ambient in enumerate(ambients_data.get("ambients", [])):
            logger.info(f"Processing ambient {i+1}/{len(ambients_data.get('ambients', []))}: {ambient.get('name')}")
            
            ambient_with_media = AmbientEnvironmentWithMedia(
                id=ambient.get("id"),
                name=ambient.get("name"),
                text=ambient.get("text"),
                image_prompt=ambient.get("image_prompt"),
                sound_prompt=ambient.get("sound_prompt"),
                voice=ambient.get("voice"),
            )
            
            # Генерация изображения
            if ambient.get("image_prompt") and not request.use_template:
                try:
                    image_filename = f"img_{generation_id}_{i+1}.jpg"
                    image_path = await _generate_image(
                        ambient.get("image_prompt"),
                        image_filename
                    )
                    ambient_with_media.image_path = f"ambients/images/{image_filename}"
                    stats["images_generated"] += 1
                    logger.info(f"Generated image: {image_filename}")
                except Exception as e:
                    ambient_with_media.image_error = str(e)
                    stats["images_failed"] += 1
                    logger.error(f"Failed to generate image: {str(e)}")
            elif ambient.get("image_prompt") and request.use_template:
                # Используем заглушку
                ambient_with_media.image_path = TEMPLATE_IMAGE_PATH
                stats["images_generated"] += 1
            
            # Генерация звука
            if ambient.get("sound_prompt") and not request.use_template:
                try:
                    sound_filename = f"sound_{generation_id}_{i+1}.mp3"
                    sound_path = await _generate_sound(
                        ambient.get("sound_prompt"),
                        sound_filename
                    )
                    ambient_with_media.sound_path = f"ambients/sounds/{sound_filename}"
                    stats["sounds_generated"] += 1
                    logger.info(f"Generated sound: {sound_filename}")
                except Exception as e:
                    ambient_with_media.sound_error = str(e)
                    stats["sounds_failed"] += 1
                    logger.error(f"Failed to generate sound: {str(e)}")
            elif ambient.get("sound_prompt") and request.use_template:
                # Используем заглушку
                ambient_with_media.sound_path = TEMPLATE_SOUND_PATH
                stats["sounds_generated"] += 1
            
            # Генерация голоса
            if ambient.get("voice") and not request.use_template:
                try:
                    voice_filename = f"voice_{generation_id}_{i+1}.mp3"
                    voice_path = await _generate_voice(
                        ambient.get("voice"),
                        voice_filename
                    )
                    ambient_with_media.voice_path = f"ambients/voices/{voice_filename}"
                    stats["voices_generated"] += 1
                    logger.info(f"Generated voice: {voice_filename}")
                except Exception as e:
                    ambient_with_media.voice_error = str(e)
                    stats["voices_failed"] += 1
                    logger.error(f"Failed to generate voice: {str(e)}")
            elif ambient.get("voice") and request.use_template:
                # Используем заглушку
                ambient_with_media.voice_path = TEMPLATE_VOICE_PATH
                stats["voices_generated"] += 1
            
            ambients_with_media.append(ambient_with_media)
        
        tools = ProfessionTools(
            title=ambients_data.get("tools", {}).get("title", "Инструменты профессии"),
            items=ambients_data.get("tools", {}).get("items", [])
        )
        
        return AmbientsWithMediaResponse(
            profession_title=ambients_data.get("profession_title", request.profession_title),
            ambients=ambients_with_media,
            tools=tools,
            json_path=f"ambients/results/{json_filename}",
            generation_stats=stats
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка генерации: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error in ambients generation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


async def _generate_image(prompt: str, filename: str) -> str:
    """Генерация изображения через Fusion Brain API"""
    try:
        api = FusionBrainAPI()
        image_base64 = api.generate_image(
            prompt=prompt,
            width=448,  # Кратно 64, близко к 400
            height=448,
            attempts=10,  # Уменьшено до 10 попыток (~100 сек макс)
            delay=10
        )
        
        # Декодируем base64 и сохраняем
        image_data = base64.b64decode(image_base64)
        image_path = IMAGES_DIR / filename
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        return str(image_path)
    except Exception as e:
        raise Exception(f"Image generation failed: {str(e)}")


async def _generate_sound(prompt: str, filename: str) -> str:
    """Генерация звука через ElevenLabs API"""
    if not settings.ELEVENLABS_API_KEY:
        raise Exception("ElevenLabs API key not configured")
    
    try:
        url = "https://api.elevenlabs.io/v1/sound-generation"
        output_format = "mp3_44100_128"
        
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": prompt,
            "duration_seconds": 8.0,  # 8 секунд
            "model_id": "eleven_text_to_sound_v2",
            "loop": True  # Для зацикливания
        }
        
        response = requests.post(
            f"{url}?output_format={output_format}",
            headers=headers,
            json=payload,
            timeout=40
        )
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs API error: {response.text}")
        
        # Сохраняем звук
        sound_path = SOUNDS_DIR / filename
        with open(sound_path, "wb") as f:
            f.write(response.content)
        
        return str(sound_path)
    except Exception as e:
        raise Exception(f"Sound generation failed: {str(e)}")


async def _generate_voice(text: str, filename: str) -> str:
    """Генерация голоса через ElevenLabs TTS API"""
    if not settings.ELEVENLABS_API_KEY:
        raise Exception("ElevenLabs API key not configured")
    
    try:
        # Используем русскоязычный голос
        voice_id = "JBFqnCBsd6RMkjVDRZzb"  # George - multilingual
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "output_format": "mp3_44100_128"
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=40
        )
        
        if response.status_code != 200:
            raise Exception(f"ElevenLabs TTS API error: {response.text}")
        
        # Сохраняем голос
        voice_path = VOICES_DIR / filename
        with open(voice_path, "wb") as f:
            f.write(response.content)
        
        return str(voice_path)
    except Exception as e:
        raise Exception(f"Voice generation failed: {str(e)}")


def _get_template_ambients_data(profession_title: str) -> Dict[str, Any]:
    """Возвращает шаблонные данные для тестирования"""
    return {
        "profession_title": profession_title,
        "ambients": [
            {
                "id": "ambient_1",
                "name": "Тестовое окружение 1",
                "text": "Это тестовое описание ситуации в профессии. Здесь подробно описывается, что происходит в данном окружении.",
                "image_prompt": "Professional office environment, modern workspace, realistic photography",
                "sound_prompt": "Office ambient sounds, keyboard typing, people talking",
                "voice": "Это тестовая фраза для генерации голоса."
            },
            {
                "id": "ambient_2",
                "name": "Тестовое окружение 2",
                "text": "Еще одно описание рабочей ситуации. Текст помогает понять атмосферу профессии.",
                "image_prompt": "Team meeting in conference room, collaborative work, professional photo",
                "sound_prompt": "Meeting room sounds, discussions, presentation",
            },
            {
                "id": "ambient_3",
                "name": "Тестовое окружение 3",
                "text": "Третье окружение показывает другой аспект работы в данной профессии.",
                "voice": "Давайте обсудим этот проект подробнее."
            }
        ],
        "tools": {
            "title": "Инструменты профессии",
            "items": [
                "💻 Инструмент 1 - описание",
                "📊 Инструмент 2 - описание",
                "🔧 Инструмент 3 - описание",
            ]
        }
    }


@router.get("/media/{media_type}/{filename}")
async def get_ambient_media_file(
    media_type: str,
    filename: str,
    token: Optional[str] = Query(None, description="JWT токен")
):
    """
    Получение медиа файла (изображение, звук, голос)
    
    media_type: images, sounds, voices, results
    token: JWT токен из query параметра
    """
    # Проверяем токен
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен не предоставлен",
        )
    
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
        )
    
    # Логируем параметры
    logger.info(f"Accessing media: media_type={media_type}, filename={filename}")
    
    # Определяем директорию
    # Шаблоны и обычные файлы лежат в одних директориях
    if media_type == "images":
        file_path = IMAGES_DIR / filename
        media_type_str = "image/jpeg"
    elif media_type == "sounds":
        file_path = SOUNDS_DIR / filename
        media_type_str = "audio/mpeg"
    elif media_type == "voices":
        file_path = VOICES_DIR / filename
        media_type_str = "audio/mpeg"
    elif media_type == "results":
        file_path = JSON_DIR / filename
        media_type_str = "application/json"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный тип медиа"
        )
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Файл не найден: {file_path}"
        )
    
    return FileResponse(
        path=file_path,
        media_type=media_type_str,
        filename=filename
    )


@router.post("/generate-ambient-media", response_model=GenerateMediaForAmbientResponse)
async def generate_media_for_ambient(
    request: GenerateMediaForAmbientRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Генерация медиа файлов для конкретного окружения
    Используется для постепенной загрузки медиа после отображения текста
    """
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    response = GenerateMediaForAmbientResponse(
        ambient_id=request.ambient_id
    )
    
    # Создаем уникальный ID для файлов
    generation_id = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{request.ambient_id}"
    
    # Генерация изображения
    if request.image_prompt and not request.use_template:
        try:
            image_filename = f"img_{generation_id}.jpg"
            await _generate_image(request.image_prompt, image_filename)
            response.image_path = f"ambients/images/{image_filename}"
            logger.info(f"Generated image for ambient {request.ambient_id}, path: {response.image_path}")
        except Exception as e:
            response.image_error = str(e)
            logger.error(f"Failed to generate image: {str(e)}")
    elif request.image_prompt and request.use_template:
        response.image_path = TEMPLATE_IMAGE_PATH
        logger.info(f"Using template image, path: {response.image_path}")
    
    # Генерация звука
    if request.sound_prompt and not request.use_template:
        try:
            sound_filename = f"sound_{generation_id}.mp3"
            await _generate_sound(request.sound_prompt, sound_filename)
            response.sound_path = f"ambients/sounds/{sound_filename}"
            logger.info(f"Generated sound for ambient {request.ambient_id}, path: {response.sound_path}")
        except Exception as e:
            response.sound_error = str(e)
            logger.error(f"Failed to generate sound: {str(e)}")
    elif request.sound_prompt and request.use_template:
        response.sound_path = TEMPLATE_SOUND_PATH
        logger.info(f"Using template sound, path: {response.sound_path}")
    
    # Генерация голоса
    if request.voice_text and not request.use_template:
        try:
            voice_filename = f"voice_{generation_id}.mp3"
            await _generate_voice(request.voice_text, voice_filename)
            response.voice_path = f"ambients/voices/{voice_filename}"
            logger.info(f"Generated voice for ambient {request.ambient_id}, path: {response.voice_path}")
        except Exception as e:
            response.voice_error = str(e)
            logger.error(f"Failed to generate voice: {str(e)}")
    elif request.voice_text and request.use_template:
        response.voice_path = TEMPLATE_VOICE_PATH
        logger.info(f"Using template voice, path: {response.voice_path}")
    
    logger.info(f"Returning response: image_path={response.image_path}, sound_path={response.sound_path}, voice_path={response.voice_path}")
    return response

