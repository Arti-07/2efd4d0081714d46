from pydantic import BaseModel, Field
from typing import Optional


class ImageGenerateRequest(BaseModel):
    """Запрос на генерацию изображения"""
    prompt: str = Field(
        ...,
        description="Текстовое описание изображения (макс 1000 символов)",
        min_length=1,
        max_length=1000,
        examples=["Пушистый кот в очках"]
    )
    width: int = Field(
        default=1024,
        description="Ширина изображения (кратно 64, макс 1024)",
        ge=64,
        le=1024
    )
    height: int = Field(
        default=1024,
        description="Высота изображения (кратно 64, макс 1024)",
        ge=64,
        le=1024
    )
    style: Optional[str] = Field(
        default=None,
        description="Стиль генерации (например: ANIME, DEFAULT)",
        examples=["ANIME", "KANDINSKY", "UHD"]
    )
    negative_prompt: Optional[str] = Field(
        default=None,
        description="Негативный промпт - что не должно быть на изображении",
        max_length=1000,
        examples=["яркие цвета, кислотность, высокая контрастность"]
    )


class ImageGenerateResponse(BaseModel):
    """Ответ с сгенерированным изображением"""
    image_base64: str = Field(
        ...,
        description="Изображение в формате Base64"
    )
    prompt: str = Field(
        ...,
        description="Использованный промпт"
    )
    width: int = Field(
        ...,
        description="Ширина изображения"
    )
    height: int = Field(
        ...,
        description="Высота изображения"
    )
    style: Optional[str] = Field(
        default=None,
        description="Использованный стиль"
    )


class StyleInfo(BaseModel):
    """Информация о стиле генерации"""
    name: str = Field(
        ...,
        description="Название стиля"
    )
    title: Optional[str] = Field(
        default=None,
        description="Отображаемое название"
    )
    titleEn: Optional[str] = Field(
        default=None,
        description="Название на английском"
    )
    image: Optional[str] = Field(
        default=None,
        description="Превью изображение стиля"
    )


class StylesResponse(BaseModel):
    """Список доступных стилей"""
    styles: list[StyleInfo] = Field(
        ...,
        description="Список стилей"
    )
    total: int = Field(
        ...,
        description="Общее количество стилей"
    )


class ServiceStatusResponse(BaseModel):
    """Статус доступности сервиса"""
    available: bool = Field(
        ...,
        description="Доступен ли сервис"
    )
    status: Optional[str] = Field(
        default=None,
        description="Статус сервиса"
    )

