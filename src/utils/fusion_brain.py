import json
import time
import base64
from typing import Optional, List

import requests

from src.config import settings


class FusionBrainAPI:
    """
    Класс для работы с Fusion Brain API (Kandinsky)
    Генерация изображений на основе текстового описания
    """

    def __init__(self, url: str = None, api_key: str = None, secret_key: str = None):
        self.URL = url or settings.FUSION_BRAIN_API_URL
        self.API_KEY = api_key or settings.FUSION_BRAIN_API_KEY
        self.SECRET_KEY = secret_key or settings.FUSION_BRAIN_SECRET_KEY
        
        if not self.API_KEY or not self.SECRET_KEY:
            raise ValueError("Fusion Brain API ключи не настроены в переменных окружения")
        
        self.AUTH_HEADERS = {
            'X-Key': f'Key {self.API_KEY}',
            'X-Secret': f'Secret {self.SECRET_KEY}',
        }

    def get_pipeline(self) -> str:
        """
        Получение ID доступной модели генерации
        
        Returns:
            str: UUID модели Kandinsky
        """
        response = requests.get(
            self.URL + 'key/api/v1/pipelines',
            headers=self.AUTH_HEADERS
        )
        response.raise_for_status()
        data = response.json()
        
        if not data:
            raise ValueError("Нет доступных моделей")
        
        return data[0]['id']

    def generate(
        self,
        prompt: str,
        pipeline_id: str,
        images: int = 1,
        width: int = 1024,
        height: int = 1024,
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None
    ) -> str:
        """
        Запуск генерации изображения
        
        Args:
            prompt: Текстовое описание изображения
            pipeline_id: ID модели генерации
            images: Количество изображений (только 1)
            width: Ширина изображения (кратно 64, макс 1024)
            height: Высота изображения (кратно 64, макс 1024)
            style: Стиль генерации (опционально)
            negative_prompt: Негативный промпт (опционально)
            
        Returns:
            str: UUID задачи генерации
        """
        if len(prompt) > 1000:
            raise ValueError("Промпт не должен превышать 1000 символов")
        
        if images != 1:
            raise ValueError("Можно генерировать только 1 изображение за раз")
        
        if width > 1024 or height > 1024:
            raise ValueError("Максимальный размер изображения 1024x1024")
        
        if width % 64 != 0 or height % 64 != 0:
            raise ValueError("Размеры должны быть кратны 64")
        
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": prompt
            }
        }
        
        if style:
            params["style"] = style
        
        if negative_prompt:
            params["negativePromptDecoder"] = negative_prompt

        data = {
            'pipeline_id': (None, pipeline_id),
            'params': (None, json.dumps(params), 'application/json')
        }
        
        response = requests.post(
            self.URL + 'key/api/v1/pipeline/run',
            headers=self.AUTH_HEADERS,
            files=data
        )
        response.raise_for_status()
        result = response.json()
        
        if 'uuid' not in result:
            raise ValueError(f"Ошибка запуска генерации: {result}")
        
        return result['uuid']

    def check_generation(
        self,
        request_id: str,
        attempts: int = 30,
        delay: int = 10
    ) -> Optional[List[str]]:
        """
        Проверка статуса генерации и получение результата
        
        Args:
            request_id: UUID задачи генерации
            attempts: Количество попыток проверки
            delay: Задержка между попытками в секундах
            
        Returns:
            List[str]: Список base64 изображений или None при ошибке
        """
        max_attempts = attempts  # Сохраняем для проверки
        while attempts > 0:
            try:
                response = requests.get(
                    self.URL + 'key/api/v1/pipeline/status/' + request_id,
                    headers=self.AUTH_HEADERS,
                    timeout=15  # Таймаут для запроса
                )
                response.raise_for_status()
                data = response.json()
                
                status = data.get('status')
                
                if status == 'DONE':
                    result = data.get('result', {})
                    
                    # Проверка на цензуру
                    if result.get('censored', False):
                        raise ValueError("Изображение не прошло модерацию контента")
                    
                    files = result.get('files')
                    if files:
                        return files
                    else:
                        raise ValueError("Генерация завершена, но файлы не получены")
                
                elif status == 'FAIL':
                    error = data.get('errorDescription', 'Неизвестная ошибка')
                    raise ValueError(f"Ошибка генерации: {error}")
                
                elif status == 'INITIAL' or status == 'PROCESSING':
                    attempts -= 1
                    if attempts > 0:
                        time.sleep(delay)
                else:
                    raise ValueError(f"Неизвестный статус: {status}")
                    
            except requests.exceptions.HTTPError as e:
                # Если 403 или другая HTTP ошибка - прерываем цикл
                if e.response.status_code == 403:
                    raise ValueError(f"API отклонил запрос (403 Forbidden). Возможно превышен лимит запросов.")
                elif e.response.status_code >= 500:
                    # Серверная ошибка - можем попробовать еще раз
                    attempts -= 1
                    if attempts > 0:
                        time.sleep(delay)
                    else:
                        raise ValueError(f"Серверная ошибка API: {e.response.status_code}")
                else:
                    raise ValueError(f"HTTP ошибка: {e.response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                # Другие ошибки сети
                attempts -= 1
                if attempts > 0:
                    time.sleep(delay)
                else:
                    raise ValueError(f"Ошибка сети: {str(e)}")
        
        raise TimeoutError(f"Превышено время ожидания генерации ({max_attempts * delay} сек)")

    def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        style: Optional[str] = None,
        negative_prompt: Optional[str] = None,
        attempts: int = 30,
        delay: int = 10
    ) -> str:
        """
        Полный цикл генерации изображения
        
        Args:
            prompt: Текстовое описание
            width: Ширина (кратно 64, макс 1024)
            height: Высота (кратно 64, макс 1024)
            style: Стиль генерации
            negative_prompt: Негативный промпт
            attempts: Попытки проверки статуса
            delay: Задержка между проверками
            
        Returns:
            str: Base64 изображение
        """
        pipeline_id = self.get_pipeline()
        
        uuid = self.generate(
            prompt=prompt,
            pipeline_id=pipeline_id,
            images=1,
            width=width,
            height=height,
            style=style,
            negative_prompt=negative_prompt
        )
        
        files = self.check_generation(uuid, attempts=attempts, delay=delay)
        
        if not files or len(files) == 0:
            raise ValueError("Не удалось получить сгенерированное изображение")
        
        return files[0]

    def check_availability(self) -> dict:
        """
        Проверка доступности сервиса
        
        Returns:
            dict: Статус сервиса
        """
        response = requests.get(
            self.URL + 'key/api/v1/pipeline/availability',
            headers=self.AUTH_HEADERS
        )
        response.raise_for_status()
        return response.json()

    def get_styles(self) -> List[dict]:
        """
        Получение списка доступных стилей
        
        Returns:
            List[dict]: Список стилей
        """
        response = requests.get('https://cdn.fusionbrain.ai/static/styles/key')
        response.raise_for_status()
        return response.json()

