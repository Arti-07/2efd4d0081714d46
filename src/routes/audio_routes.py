from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import requests
import os
from pathlib import Path

from src.models.audio_model import SoundGenerationRequest, TextToSpeechRequest, AudioResponse
from src.config import settings

router = APIRouter(prefix="/audio", tags=["Audio Generation"])

# Директория для сохранения аудио файлов
AUDIO_DIR = Path("data/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/generate-sound", response_model=AudioResponse)
async def generate_sound(request: SoundGenerationRequest):
    """
    Генерация звуковых эффектов через ElevenLabs API
    """
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ElevenLabs API ключ не настроен"
        )
    
    # Конфигурация запроса
    config = {
        "text": request.text,
        "duration_seconds": request.duration_seconds,
        "model_id": "eleven_text_to_sound_v2",
        "loop": request.loop,
    }
    
    if request.prompt_influence is not None:
        config["prompt_influence"] = request.prompt_influence
    
    # API endpoint
    url = "https://api.elevenlabs.io/v1/sound-generation"
    output_format = "mp3_44100_128"
    
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    url_with_params = f"{url}?output_format={output_format}"
    
    try:
        response = requests.post(
            url_with_params,
            headers=headers,
            json=config,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ElevenLabs API error: {response.text}"
            )
        
        # Сохранение аудио файла
        filename = f"sound_{abs(hash(request.text))}.mp3"
        output_path = AUDIO_DIR / filename
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return AudioResponse(
            message="Звуковой эффект успешно создан",
            file_path=filename
        )
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запросе к ElevenLabs API: {str(e)}"
        )


@router.post("/text-to-speech", response_model=AudioResponse)
async def text_to_speech(request: TextToSpeechRequest):
    """
    Преобразование текста в речь через ElevenLabs API
    """
    if not settings.ELEVENLABS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ElevenLabs API ключ не настроен"
        )
    
    # API endpoint
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{request.voice_id}"
    output_format = "mp3_44100_128"
    
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": request.text,
        "model_id": request.model_id,
        "output_format": output_format
    }
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ElevenLabs API error: {response.text}"
            )
        
        # Сохранение аудио файла
        filename = f"speech_{abs(hash(request.text))}.mp3"
        output_path = AUDIO_DIR / filename
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        return AudioResponse(
            message="Речь успешно создана",
            file_path=filename
        )
        
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при запросе к ElevenLabs API: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_audio(filename: str):
    """
    Скачивание сгенерированного аудио файла
    """
    file_path = AUDIO_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аудио файл не найден"
        )
    
    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename
    )

