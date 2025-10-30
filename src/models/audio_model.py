from pydantic import BaseModel, Field
from typing import Optional


class SoundGenerationRequest(BaseModel):
    text: str = Field(..., description="Описание звука для генерации")
    duration_seconds: Optional[float] = Field(5.0, ge=0.5, le=22.0, description="Длительность в секундах")
    prompt_influence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Влияние промпта (0.0-1.0)")
    loop: Optional[bool] = Field(False, description="Должен ли звук зацикливаться")


class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Текст для озвучивания")
    voice_id: Optional[str] = Field("JBFqnCBsd6RMkjVDRZzb", description="ID голоса")
    model_id: Optional[str] = Field("eleven_multilingual_v2", description="ID модели")


class AudioResponse(BaseModel):
    message: str
    file_path: str

