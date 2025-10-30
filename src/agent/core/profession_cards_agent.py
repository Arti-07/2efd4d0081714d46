# profession_cards_agent.py
import logging
import uuid
import json
from datetime import datetime
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


class ProfessionCardsAgent:
    """Agent that generates personalized profession recommendations based on personality and astrology data"""

    name: str = "profession_cards_agent"

    def __init__(
        self,
        personality_data: Optional[Dict[str, Any]] = None,
        astrology_data: Optional[Dict[str, Any]] = None,
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        max_tokens: Optional[int] = 8192,
        temperature: float = 0.4,
        top_p: float = 0.9,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ):
        self.id = f"{self.name}_{uuid.uuid4()}"
        self.logger = logging.getLogger(self.id)
        
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

    def _prepare_input_text(self) -> str:
        """Prepare combined input from personality and astrology data"""
        input_parts = []
        
        if self.personality_data:
            input_parts.append("=== ДАННЫЕ ТЕСТА ЛИЧНОСТИ ===")
            input_parts.append(json.dumps(self.personality_data, ensure_ascii=False, indent=2))
        
        if self.astrology_data:
            input_parts.append("\n=== АСТРОЛОГИЧЕСКИЙ ПРОФИЛЬ ===")
            input_parts.append(json.dumps(self.astrology_data, ensure_ascii=False, indent=2))
        
        if not input_parts:
            raise ValueError("No personality or astrology data provided")
        
        return "\n".join(input_parts)

    async def generate_profession_cards(self) -> List[Dict[str, Any]]:
        """Generate personalized profession recommendation cards"""
        self.logger.info("🚀 Starting profession cards generation")

        system_prompt = PromptLoader.get_prompt("profession_cards_prompt.txt")
        input_text = self._prepare_input_text()

        try:
            completion = await self.openai_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": config.http_referer,
                    "X-Title": config.x_title,
                },
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": input_text,
                    },
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                presence_penalty=self.presence_penalty,
                frequency_penalty=self.frequency_penalty,
            )
            
            response_content = completion.choices[0].message.content.strip()
            self.logger.debug(f"Raw response: {response_content}")
            
            # Clean and parse JSON
            cleaned_json = self._clean_json_response(response_content)
            profession_cards = json.loads(cleaned_json)
            
            # Validate response
            if not isinstance(profession_cards, list):
                raise ValueError("Response is not a list")
            
            self.logger.info(f"✅ Generated {len(profession_cards)} profession cards")
            return profession_cards

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parsing failed: {str(e)}")
            raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ Generation failed: {str(e)}")
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
        
        # Fix truncated JSON
        return self._fix_truncated_json(response)

    def _fix_truncated_json(self, truncated_str: str) -> str:
        """Fix common JSON truncation issues"""
        s = truncated_str.strip()
        
        # Remove trailing comma
        if s.endswith(','):
            s = s[:-1]
        
        # Fix unclosed objects
        if s.count('{') > s.count('}'):
            last_open = s.rfind('{')
            last_close_after = s.find('}', last_open)
            if last_close_after == -1:
                s = s[:last_open].rstrip()
                if s.endswith(','):
                    s = s[:-1]
        
        # Fix unclosed arrays
        if s.count('[') > s.count(']'):
            s += ']'
        
        # Fix unclosed objects at the end
        while s.count('{') > s.count('}'):
            s += '}'
        
        return s

