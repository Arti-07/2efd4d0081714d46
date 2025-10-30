import os
from functools import cache
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional

class AppConfig(BaseModel):
    api_key: str = Field(..., alias="API_KEY")
    model_name: str = Field(..., alias="MODEL_NAME")
    http_referer: Optional[str] = Field(None, alias="HTTP_REFERER")
    x_title: Optional[str] = Field(None, alias="X_TITLE")
    base_url: Optional[str] = Field(None, alias="BASE_URL")
    prompts_dir: Optional[str] = Field(None, alias="PROMPTS_DIR")
    system_prompt_file: Optional[str] = Field(None, alias="SYSTEM_PROMPT_FILE")

    class Config:
        # Разрешает использовать alias как имена переменных в .env
        populate_by_name = True


@cache
def get_config() -> AppConfig:
    # Пытаемся загрузить .env файл, если он существует (для разработки)
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=False)  # Не перезаписываем существующие переменные
        print(f"Загружен .env файл: {env_path}")
    else:
        # В Docker переменные окружения передаются напрямую, это нормально
        print("Используются переменные окружения (Docker/система)")

    # Передаём всё окружение в модель
    return AppConfig.model_validate(os.environ)