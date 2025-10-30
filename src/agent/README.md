# AI Agents Module

Этот модуль содержит AI-агентов для различных задач в приложении.

## Структура

```
agent/
├── core/                           # Основной код агентов
│   ├── career_navigator_agent.py   # Агент для создания карьерного пути
│   ├── profession_cards_agent.py   # Агент для генерации карточек профессий
│   └── prompts.py                  # Загрузчик промптов
├── prompts/                        # Системные промпты для агентов
│   ├── system_prompt.txt           # Промпт для career_navigator_agent
│   └── profession_cards_prompt.txt # Промпт для profession_cards_agent
├── settings.py                     # Конфигурация агентов
└── *_agent_test.py                # Тестовые файлы для агентов
```

## Существующие агенты

### 1. CareerNavigatorAgent
**Файл**: `core/career_navigator_agent.py`  
**Промпт**: `prompts/system_prompt.txt`  
**Назначение**: Создание детального карьерного плана с этапами развития

**Пример использования**:
```python
from src.agent.core.career_navigator_agent import CareerNavigatorAgent

agent = CareerNavigatorAgent(
    input_text="текст с данными пользователя",
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    temperature=0.3,
    max_tokens=2048,
)

career_plan = await agent.createCareer()
```

### 2. ProfessionCardsAgent
**Файл**: `core/profession_cards_agent.py`  
**Промпт**: `prompts/profession_cards_prompt.txt`  
**Назначение**: Генерация персонализированных карточек профессий на основе теста личности и астрологии

**Пример использования**:
```python
from src.agent.core.profession_cards_agent import ProfessionCardsAgent

agent = ProfessionCardsAgent(
    personality_data={"code": "ENTP-T", ...},
    astrology_data={"zodiac_sign": "Водолей", ...},
    temperature=0.4,
    max_tokens=2048,
)

cards = await agent.generate_profession_cards()
```

## Как добавить нового агента

### Шаг 1: Создайте файл промпта

Создайте новый файл в `prompts/`:
```
prompts/your_new_agent_prompt.txt
```

В файле определите:
- Роль агента
- Принципы работы
- Формат входных данных
- Требования к выходным данным (обычно JSON)
- Критерии качества

### Шаг 2: Создайте класс агента

Создайте новый файл в `core/`:
```python
# core/your_new_agent.py
import logging
import uuid
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from src.agent.settings import get_config
from src.agent.core.prompts import PromptLoader

config = get_config()

class YourNewAgent:
    """Описание назначения агента"""
    
    name: str = "your_new_agent"
    
    def __init__(
        self,
        input_data: Dict[str, Any],
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        max_tokens: Optional[int] = 2048,
        temperature: float = 0.3,
    ):
        self.id = f"{self.name}_{uuid.uuid4()}"
        self.logger = logging.getLogger(self.id)
        self.input_data = input_data
        self.model = config.model_name if config.model_name else model
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        client_kwargs = {
            "base_url": config.base_url.strip(),
            "api_key": config.api_key
        }
        self.openai_client = AsyncOpenAI(**client_kwargs)
    
    async def process(self) -> Any:
        """Основной метод агента"""
        self.logger.info(f"🚀 Starting {self.name}")
        
        # Загружаем промпт
        system_prompt = PromptLoader.get_prompt("your_new_agent_prompt.txt")
        
        # Подготавливаем входные данные
        user_message = self._prepare_input()
        
        try:
            completion = await self.openai_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": config.http_referer,
                    "X-Title": config.x_title,
                },
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            response = completion.choices[0].message.content.strip()
            result = self._parse_response(response)
            
            self.logger.info(f"✅ {self.name} completed")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ {self.name} failed: {str(e)}")
            raise
    
    def _prepare_input(self) -> str:
        """Подготовка входных данных для агента"""
        # Ваша логика
        pass
    
    def _parse_response(self, response: str) -> Any:
        """Парсинг ответа агента"""
        # Ваша логика
        pass
```

### Шаг 3: Создайте тестовый файл

```python
# your_new_agent_test.py
import asyncio
from src.agent.core.your_new_agent import YourNewAgent

async def main():
    agent = YourNewAgent(
        input_data={"test": "data"},
        temperature=0.3,
    )
    
    try:
        result = await agent.process()
        print("✅ Результат:", result)
    except Exception as e:
        print("❌ Ошибка:", e)

if __name__ == "__main__":
    asyncio.run(main())
```

### Шаг 4: Создайте API endpoint (опционально)

Если агент должен быть доступен через API:

1. Создайте модели в `src/models/`:
```python
# src/models/your_feature_model.py
from pydantic import BaseModel

class YourRequest(BaseModel):
    field1: str
    field2: int

class YourResponse(BaseModel):
    result: str
```

2. Создайте route в `src/routes/`:
```python
# src/routes/your_feature_routes.py
from fastapi import APIRouter, HTTPException, Depends
from src.agent.core.your_new_agent import YourNewAgent

router = APIRouter(prefix="/your-feature", tags=["Your Feature"])

@router.post("/process")
async def process_data(request: YourRequest):
    agent = YourNewAgent(input_data=request.dict())
    result = await agent.process()
    return YourResponse(result=result)
```

3. Подключите route в `src/routes/__init__.py`:
```python
from .your_feature_routes import router as your_feature_router

__all__ = [..., "your_feature_router"]
```

4. Добавьте в `main.py`:
```python
from src.routes import ..., your_feature_router

app.include_router(your_feature_router)
```

## Конфигурация

Настройки агентов задаются через переменные окружения в `.env`:

```env
API_KEY=your_api_key
MODEL_NAME=Qwen/Qwen3-235B-A22B-Instruct-2507
BASE_URL=https://api.openai.com/v1
HTTP_REFERER=http://localhost:8000
X_TITLE=Career AI
PROMPTS_DIR=prompts
SYSTEM_PROMPT_FILE=system_prompt.txt
```

## Лучшие практики

1. **Именование**: Используйте формат `{purpose}_agent.py` для файлов агентов
2. **Логирование**: Всегда логируйте начало, успех и ошибки
3. **Обработка ошибок**: Оборачивайте вызовы API в try-except
4. **Парсинг JSON**: Добавляйте методы очистки и валидации ответов
5. **Тестирование**: Создавайте тестовые файлы для каждого агента
6. **Документация**: Добавляйте docstrings и комментарии к коду
7. **Промпты**: Делайте промпты детальными и явно указывайте формат вывода

## Отладка

Для тестирования агента без API:
```bash
cd hh_final_back
python -m src.agent.your_new_agent_test
```

Для просмотра логов включите DEBUG уровень:
```python
logging.basicConfig(level=logging.DEBUG)
```

