from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests

from src.models.image_model import (
    ImageGenerateRequest,
    ImageGenerateResponse,
    StylesResponse,
    StyleInfo,
    ServiceStatusResponse
)
from src.utils.auth import verify_token
from src.utils.fusion_brain import FusionBrainAPI

router = APIRouter(prefix="/images", tags=["Image Generation"])
security = HTTPBearer()


@router.post("/generate", response_model=ImageGenerateResponse)
async def generate_image(
    request: ImageGenerateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Генерация изображения на основе текстового описания
    
    Использует Kandinsky (Fusion Brain API) для создания изображений.
    
    **Параметры:**
    - **prompt**: Текстовое описание (макс 1000 символов)
    - **width**: Ширина в пикселях (кратно 64, от 64 до 1024)
    - **height**: Высота в пикселях (кратно 64, от 64 до 1024)
    - **style**: Стиль генерации (опционально, см. /images/styles)
    - **negative_prompt**: Что не должно быть на изображении (опционально)
    
    **Возвращает:**
    - Изображение в формате Base64
    
    **Примечания:**
    - Размеры должны быть кратны 64 для лучшего качества
    - Рекомендуемые соотношения сторон: 1:1, 2:3, 3:2, 9:16, 16:9
    - Генерация может занять 30-120 секунд
    - Контент проходит модерацию
    """
    # Проверка токена
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Проверка размеров (кратность 64)
    if request.width % 64 != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ширина должна быть кратна 64. Ближайшие значения: {(request.width // 64) * 64} или {((request.width // 64) + 1) * 64}"
        )
    
    if request.height % 64 != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Высота должна быть кратна 64. Ближайшие значения: {(request.height // 64) * 64} или {((request.height // 64) + 1) * 64}"
        )
    
    try:
        # Инициализация API
        api = FusionBrainAPI()
        
        # Генерация изображения
        image_base64 = api.generate_image(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            style=request.style,
            negative_prompt=request.negative_prompt,
            attempts=30,  # 30 попыток * 10 сек = 5 минут максимум
            delay=10
        )
        
        return ImageGenerateResponse(
            image_base64=image_base64,
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            style=request.style
        )
        
    except ValueError as e:
        # Ошибки валидации и API
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except TimeoutError as e:
        # Таймаут генерации
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=str(e)
        )
    except requests.exceptions.HTTPError as e:
        # HTTP ошибки от Fusion Brain API
        status_code = e.response.status_code if hasattr(e, 'response') else 500
        
        if status_code == 401:
            detail = "Ошибка авторизации Fusion Brain API. Проверьте API ключи."
        elif status_code == 404:
            detail = "Ресурс не найден в Fusion Brain API"
        elif status_code == 415:
            detail = "Неподдерживаемый формат данных"
        else:
            detail = f"Ошибка Fusion Brain API: {str(e)}"
        
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail
        )
    except Exception as e:
        # Прочие ошибки
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/styles", response_model=StylesResponse)
async def get_available_styles(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Получение списка доступных стилей генерации
    
    **Возвращает:**
    - Список стилей с названиями и превью
    
    **Примеры стилей:**
    - KANDINSKY - стандартный стиль
    - ANIME - аниме стиль
    - UHD - ультра четкость
    - и другие
    """
    # Проверка токена
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        api = FusionBrainAPI()
        styles_data = api.get_styles()
        
        styles = []
        for style in styles_data:
            styles.append(StyleInfo(
                name=style.get("name", ""),
                title=style.get("title"),
                titleEn=style.get("titleEn"),
                image=style.get("image")
            ))
        
        return StylesResponse(
            styles=styles,
            total=len(styles)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения стилей: {str(e)}"
        )


@router.get("/status", response_model=ServiceStatusResponse)
async def check_service_status(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Проверка доступности сервиса генерации
    
    **Возвращает:**
    - Статус доступности сервиса
    
    **Примечание:**
    - При высокой нагрузке сервис может быть временно недоступен
    - Рекомендуется проверять статус перед отправкой задачи на генерацию
    """
    # Проверка токена
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        api = FusionBrainAPI()
        status_data = api.check_availability()
        
        # Проверяем статус
        pipeline_status = status_data.get("pipeline_status")
        
        if pipeline_status == "DISABLED_BY_QUEUE":
            available = False
            status_msg = "Сервис временно недоступен из-за высокой нагрузки"
        else:
            available = True
            status_msg = "Сервис доступен"
        
        return ServiceStatusResponse(
            available=available,
            status=status_msg
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка проверки статуса: {str(e)}"
        )

