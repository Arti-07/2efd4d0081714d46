# profession_ambients_agent.py
"""
ProfessionAmbientsAgent - агент для генерации иммерсивных окружений профессии

Этот агент создает несколько реалистичных окружений (амбиентов) для выбранной профессии,
используя данные о личности, астрологии пользователя и ответы на уточняющие вопросы.

Структура выходных данных:
{
  "profession_title": "Название профессии",
  "ambients": [
    {
      "id": "ambient_1",
      "name": "Название окружения",
      "text": "Описание ситуации",
      "image_prompt": "Промпт для изображения (опционально)",
      "sound_prompt": "Промпт для звуков (опционально)",
      "voice": "Текст голоса (опционально)"
    }
  ],
  "tools": {
    "title": "Инструменты профессии",
    "items": ["🔧 Инструмент 1", "📱 Инструмент 2", ...]
  }
}

Использование:
    agent = ProfessionAmbientsAgent(
        profession_title="Программист",
        personality_data={...},
        astrology_data={...},
        clarifying_data={...}
    )
    result = await agent.generate_ambients()

API Endpoint: POST /vibe/ambients
"""
import logging
import uuid
import json
from typing import Optional, List, Dict, Any

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


class ProfessionAmbientsAgent:
    """Agent that generates immersive professional environments (ambients) for a chosen profession"""

    name: str = "profession_ambients_agent"

    def __init__(
        self,
        profession_title: str,
        personality_data: Optional[Dict[str, Any]] = None,
        astrology_data: Optional[Dict[str, Any]] = None,
        clarifying_data: Optional[Dict[str, Any]] = None,
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        max_tokens: Optional[int] = 8192,
        temperature: float = 0.6,
        top_p: float = 0.9,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ):
        self.id = f"{self.name}_{uuid.uuid4()}"
        self.logger = logging.getLogger(self.id)
        
        self.profession_title = profession_title
        self.personality_data = personality_data
        self.astrology_data = astrology_data
        self.clarifying_data = clarifying_data
        
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
        
        # Format clarifying info (questions and answers)
        clarifying_info = "Не указана"
        if self.clarifying_data:
            if isinstance(self.clarifying_data, dict) and "questions" in self.clarifying_data:
                # Format questions and answers nicely
                formatted_qa = []
                for q in self.clarifying_data.get("questions", []):
                    question_text = q.get("question", "")
                    answer = q.get("answer", "Не указан")
                    formatted_qa.append(f"Q: {question_text}\nA: {answer}")
                clarifying_info = "\n\n".join(formatted_qa)
            else:
                clarifying_info = json.dumps(self.clarifying_data, ensure_ascii=False, indent=2)
        
        return {
            "profession_title": self.profession_title,
            "personality_info": personality_info,
            "astrology_info": astrology_info,
            "clarifying_info": clarifying_info,
        }

    async def generate_ambients(self) -> Dict[str, Any]:
        """Generate professional environments (ambients) for the profession"""
        self.logger.info(f"🚀 Generating ambients for profession: {self.profession_title}")

        # Load prompt template
        prompt_template = PromptLoader.get_prompt("profession_ambients_prompt.txt")
        
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
            self.logger.debug(f"Raw response preview: {response_content[:500]}...")
            
            # Clean and parse JSON
            cleaned_json = self._clean_json_response(response_content)
            ambients_data = json.loads(cleaned_json)
            
            # Validate response structure
            if "ambients" not in ambients_data:
                raise ValueError("Response missing 'ambients' field")
            
            if not isinstance(ambients_data["ambients"], list):
                raise ValueError("'ambients' field is not a list")
            
            if "tools" not in ambients_data:
                raise ValueError("Response missing 'tools' field")
            
            ambients_count = len(ambients_data["ambients"])
            self.logger.info(f"✅ Generated {ambients_count} professional ambients")
            return ambients_data

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

