# profession_info_agent.py
"""
ProfessionInfoAgent - агент для генерации детальной информации о профессии

Этот агент создает полную информацию о выбранной профессии, включая:
- Распорядок рабочего дня
- Стек технологий и инструментов
- Польза для компании
- Пути роста (junior → senior)
- Перспективность направления
- Количество вакансий и конкурентность
- Дополнительные карточки с описанием профессии

Структура выходных данных:
{
  "profession_title": "Название профессии",
  "cards": [
    {
      "id": "card_1",
      "type": "daily_schedule",
      "title": "Типичный рабочий день",
      "content": {
        "schedule": [
          {"time": "9:00", "activity": "Описание", "icon": "🌅"},
          ...
        ]
      }
    },
    {
      "id": "card_2",
      "type": "tech_stack",
      "title": "Стек технологий",
      "content": {
        "categories": [
          {"name": "Языки программирования", "items": ["Python", "JavaScript"]},
          ...
        ]
      }
    },
    {
      "id": "card_3",
      "type": "company_value",
      "title": "Польза для компании",
      "content": {
        "metrics": [
          {"metric": "Сокращение времени простоя", "value": "30%", "icon": "⏱️"},
          ...
        ]
      }
    },
    {
      "id": "card_4",
      "type": "career_path",
      "title": "Пути роста",
      "content": {
        "levels": [
          {"level": "Junior", "description": "...", "duration": "1-2 года", "salary_range": "..."},
          {"level": "Middle", "description": "...", "duration": "2-3 года", "salary_range": "..."},
          {"level": "Senior", "description": "...", "duration": "3-5 лет", "salary_range": "..."},
          {"level": "Lead/Architect", "description": "...", "duration": "5+ лет", "salary_range": "..."}
        ]
      }
    },
    {
      "id": "card_5",
      "type": "market_overview",
      "title": "Рынок и перспективы",
      "content": {
        "demand": "Высокий/Средний/Низкий",
        "demand_description": "...",
        "vacancies_count": "5000+ вакансий",
        "competition": "Средняя конкуренция",
        "competition_level": 6,
        "growth_potential": 9,
        "future_outlook": "Описание перспектив",
        "salary_range": "от 80,000 до 200,000 руб/мес"
      }
    },
    {
      "id": "card_6",
      "type": "skills",
      "title": "Необходимые навыки",
      "content": {
        "hard_skills": ["Навык 1", "Навык 2", ...],
        "soft_skills": ["Навык 1", "Навык 2", ...]
      }
    },
    {
      "id": "card_7",
      "type": "education",
      "title": "Образование и обучение",
      "content": {
        "formal_education": "Описание требуемого образования",
        "courses": ["Курс 1", "Курс 2", ...],
        "learning_time": "Примерный срок обучения"
      }
    },
    {
      "id": "card_8",
      "type": "pros_cons",
      "title": "Плюсы и минусы",
      "content": {
        "pros": ["Плюс 1", "Плюс 2", ...],
        "cons": ["Минус 1", "Минус 2", ...]
      }
    }
  ]
}

Использование:
    agent = ProfessionInfoAgent(
        profession_title="Программист",
        profession_description="...",
        personality_data={...},
        astrology_data={...}
    )
    result = await agent.generate_info()

API Endpoint: POST /vibe/profession-info
"""
import logging
import uuid
import json
from typing import Optional, Dict, Any

from openai import AsyncOpenAI

from src.agent.settings import get_config
from src.agent.core.prompts import PromptLoader

logging.basicConfig(
    level=logging.INFO,
    encoding="utf-8",
    format="%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

config = get_config()


class ProfessionInfoAgent:
    """Agent that generates detailed information about a profession"""

    name: str = "profession_info_agent"

    def __init__(
        self,
        profession_title: str,
        profession_description: Optional[str] = None,
        personality_data: Optional[Dict[str, Any]] = None,
        astrology_data: Optional[Dict[str, Any]] = None,
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        max_tokens: Optional[int] = 8192,
        temperature: float = 0.5,
        top_p: float = 0.9,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ):
        self.id = f"{self.name}_{uuid.uuid4()}"
        self.logger = logging.getLogger(self.id)
        
        self.profession_title = profession_title
        self.profession_description = profession_description or ""
        self.personality_data = personality_data
        self.astrology_data = astrology_data
        
        self.model = config.model_name if config.model_name else model
        self.max_tokens = max_tokens
        self.temperature = temperature 
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty

        client_kwargs = {"base_url": config.base_url.strip(), "api_key": config.api_key}
        self.openai_client = AsyncOpenAI(**client_kwargs)

    def _prepare_prompt_context(self) -> Dict[str, str]:
        """Prepare context for prompt template"""
        
        # Format personality info
        personality_info = "Не указана"
        if self.personality_data:
            personality_info = json.dumps(self.personality_data, ensure_ascii=False, indent=2)
        
        # Format astrology info
        astrology_info = "Не указана"
        if self.astrology_data:
            astrology_info = json.dumps(self.astrology_data, ensure_ascii=False, indent=2)
        
        return {
            "profession_title": self.profession_title,
            "profession_description": self.profession_description,
            "personality_info": personality_info,
            "astrology_info": astrology_info,
        }

    async def generate_info(self) -> Dict[str, Any]:
        """Generate detailed profession information"""
        self.logger.info(f"🚀 Generating detailed info for profession: {self.profession_title}")

        # Load prompt template
        prompt_template = PromptLoader.get_prompt("profession_info_prompt.txt")
        
        # Fill in context
        context = self._prepare_prompt_context()
        prompt = prompt_template.format(**context)

        try:
            completion = await self.openai_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": config.http_referer,
                    "X-Title": config.x_title,
                },
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                presence_penalty=self.presence_penalty,
                frequency_penalty=self.frequency_penalty,
            )
            
            response_content = completion.choices[0].message.content.strip()
            self.logger.debug(f"Raw response length: {len(response_content)}")
            
            # Clean and parse JSON
            cleaned_json = self._clean_json_response(response_content)
            info_data = json.loads(cleaned_json)
            
            # Validate response structure
            if "profession_title" not in info_data:
                raise ValueError("Response missing 'profession_title' field")
            
            if "cards" not in info_data or not isinstance(info_data["cards"], list):
                raise ValueError("Response missing or invalid 'cards' field")
            
            cards_count = len(info_data["cards"])
            self.logger.info(f"✅ Generated {cards_count} information cards")
            return info_data

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parsing failed: {str(e)}")
            self.logger.error(f"Attempted to parse: {cleaned_json[:1000]}")
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ Generation failed: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise

    def _clean_json_response(self, response: str) -> str:
        """Clean response to extract valid JSON"""
        # Remove markdown code blocks if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        # Strip whitespace
        response = response.strip()
        
        # Find first { (start of JSON)
        json_start = response.find('{')
        if json_start > 0:
            response = response[json_start:]
        
        # Find last } (end of JSON)
        json_end = response.rfind('}')
        if json_end > 0:
            response = response[:json_end + 1]
        
        # Fix common issues
        return self._fix_json_issues(response)

    def _fix_json_issues(self, json_str: str) -> str:
        """Fix common JSON issues"""
        s = json_str.strip()
        
        # Remove trailing comma before closing brace/bracket
        s = s.replace(',}', '}').replace(',]', ']')
        
        # Fix unclosed objects
        if s.count('{') > s.count('}'):
            s += '}' * (s.count('{') - s.count('}'))
        
        # Fix unclosed arrays
        if s.count('[') > s.count(']'):
            s += ']' * (s.count('[') - s.count(']'))
        
        return s


