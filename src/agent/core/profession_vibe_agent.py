# profession_vibe_agent.py
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


class ProfessionVibeAgent:
    """Agent that generates clarifying questions about a chosen profession"""

    name: str = "profession_vibe_agent"

    def __init__(
        self,
        profession_title: str,
        personality_data: Optional[Dict[str, Any]] = None,
        astrology_data: Optional[Dict[str, Any]] = None,
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        max_tokens: Optional[int] = 4096,
        temperature: float = 0.5,
        top_p: float = 0.9,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ):
        self.id = f"{self.name}_{uuid.uuid4()}"
        self.logger = logging.getLogger(self.id)
        
        self.profession_title = profession_title
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
        personality_info = "Не указана"
        if self.personality_data:
            personality_info = f"{self.personality_data.get('code', '')} - {self.personality_data.get('personality_type', '')}"
        
        astrology_info = "Не указана"
        if self.astrology_data:
            astrology_info = f"{self.astrology_data.get('zodiac_sign', '')} ({self.astrology_data.get('element', '')})"
        
        return {
            "profession_title": self.profession_title,
            "personality_info": personality_info,
            "astrology_info": astrology_info,
        }

    async def generate_questions(self) -> Dict[str, Any]:
        """Generate clarifying questions about the profession"""
        self.logger.info(f"🚀 Generating questions for profession: {self.profession_title}")

        # Load prompt template
        prompt_template = PromptLoader.get_prompt("profession_vibe_prompt.txt")
        
        # Fill in context
        context = self._prepare_prompt_context()
        prompt = prompt_template.format(**context)

        try:
            # Пробуем использовать JSON mode если модель поддерживает
            request_params = {
                "extra_headers": {
                    "HTTP-Referer": config.http_referer,
                    "X-Title": config.x_title,
                },
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty,
            }
            
            # Пробуем добавить response_format для JSON mode (не все модели поддерживают)
            try:
                request_params["response_format"] = {"type": "json_object"}
            except:
                pass
            
            completion = await self.openai_client.chat.completions.create(**request_params)
            
            response_content = completion.choices[0].message.content.strip()
            self.logger.info(f"Raw response length: {len(response_content)}")
            self.logger.debug(f"Raw response: {response_content[:500]}...")
            
            # Clean and parse JSON
            cleaned_json = self._clean_json_response(response_content)
            self.logger.debug(f"Cleaned JSON: {cleaned_json[:500]}...")
            questions_data = json.loads(cleaned_json)
            
            # Validate response structure
            if "questions" not in questions_data:
                raise ValueError("Response missing 'questions' field")
            
            if not isinstance(questions_data["questions"], list):
                raise ValueError("'questions' field is not a list")
            
            self.logger.info(f"✅ Generated {len(questions_data['questions'])} questions")
            return questions_data

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
        
        # Find first { or [ (start of JSON)
        json_start = -1
        for i, char in enumerate(response):
            if char in ['{', '[']:
                json_start = i
                break
        
        if json_start > 0:
            response = response[json_start:]
        
        # Find last } or ] (end of JSON)
        json_end = -1
        for i in range(len(response) - 1, -1, -1):
            if response[i] in ['}', ']']:
                json_end = i
                break
        
        if json_end > 0:
            response = response[:json_end + 1]
        
        return response.strip()

