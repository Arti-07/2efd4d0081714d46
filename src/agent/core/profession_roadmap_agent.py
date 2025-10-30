# profession_roadmap_agent.py
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


class ProfessionRoadmapAgent:
    """Agent that generates comprehensive career roadmap for a specific profession"""

    name: str = "profession_roadmap_agent"

    def __init__(
        self,
        profession_title: str,
        personality_data: Optional[Dict[str, Any]] = None,
        astrology_data: Optional[Dict[str, Any]] = None,
        current_level: Optional[str] = None,
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        max_tokens: Optional[int] = 16384,
        temperature: float = 0.4,
        top_p: float = 0.9,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ):
        self.id = f"{self.name}_{uuid.uuid4()}"
        self.logger = logging.getLogger(self.id)
        
        self.profession_title = profession_title
        self.personality_data = personality_data
        self.astrology_data = astrology_data
        self.current_level = current_level
        
        self.model = config.model_name if config.model_name else model
        self.max_tokens = max_tokens
        self.temperature = temperature 
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty

        client_kwargs = {"base_url": config.base_url.strip(), "api_key": config.api_key}
        self.openai_client = AsyncOpenAI(**client_kwargs)

    def _prepare_input_text(self) -> str:
        """Prepare combined input from profession, personality and astrology data"""
        input_parts = []
        
        # Profession
        input_parts.append(f"=== ЦЕЛЕВАЯ ПРОФЕССИЯ ===")
        input_parts.append(f"Профессия: {self.profession_title}")
        
        if self.current_level:
            input_parts.append(f"Текущий уровень: {self.current_level}")
        
        # Personality data
        if self.personality_data:
            input_parts.append("\n=== ДАННЫЕ ТЕСТА ЛИЧНОСТИ ===")
            input_parts.append(json.dumps(self.personality_data, ensure_ascii=False, indent=2))
        
        # Astrology data
        if self.astrology_data:
            input_parts.append("\n=== АСТРОЛОГИЧЕСКИЙ ПРОФИЛЬ ===")
            input_parts.append(json.dumps(self.astrology_data, ensure_ascii=False, indent=2))
        
        return "\n".join(input_parts)

    async def generate_roadmap(self) -> Dict[str, Any]:
        """Generate comprehensive career roadmap"""
        self.logger.info(f"🚀 Starting roadmap generation for: {self.profession_title}")

        system_prompt = PromptLoader.get_prompt("profession_roadmap_prompt.txt")
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
            self.logger.debug(f"Raw response length: {len(response_content)} chars")
            
            # Clean and parse JSON
            cleaned_json = self._clean_json_response(response_content)
            roadmap_data = json.loads(cleaned_json)
            
            # Validate response structure
            if not isinstance(roadmap_data, dict):
                raise ValueError("Response is not a dictionary")
            
            required_fields = ["profession", "overview", "stages"]
            for field in required_fields:
                if field not in roadmap_data:
                    raise ValueError(f"Missing required field: {field}")
            
            self.logger.info(f"✅ Generated roadmap with {len(roadmap_data.get('stages', []))} stages")
            return roadmap_data

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parsing failed: {str(e)}")
            self.logger.error(f"Failed content preview: {response_content[:500]}...")
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
        
        # Fix unclosed arrays
        if s.count('[') > s.count(']'):
            diff = s.count('[') - s.count(']')
            s += ']' * diff
        
        # Fix unclosed objects
        if s.count('{') > s.count('}'):
            diff = s.count('{') - s.count('}')
            s += '}' * diff
        
        return s

