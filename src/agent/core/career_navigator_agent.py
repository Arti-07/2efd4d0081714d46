# api_agent.py
import logging
import uuid
from datetime import datetime
from typing import Optional, AsyncGenerator

import json

import httpx
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


class CareerNavigatorAgent:
    """Agent that create your career"""

    name: str = "career_navigator_agent"

    def __init__(
        self,
        input_text: str,
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        max_tokens: Optional[int] = 512,
        temperature: float = 0.3,
        top_p: float = 0.9,
        presence_penalty: float = 0.0,
        frequency_penalty: float = 0.0,
    ):
        self.id = f"{self.name}_{uuid.uuid4()}"
        self.logger = logging.getLogger(self.id)
        self.input_text = input_text
        self.model = config.model_name if config.model_name else model

        self.max_tokens = max_tokens
        self.temperature = temperature 
        self.top_p = top_p
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty

        client_kwargs = {"base_url": config.base_url.strip(), "api_key": config.api_key}

        self.openai_client = AsyncOpenAI(**client_kwargs)

    async def createCareer(self) -> str:
        """Generate you individual career."""
        self.logger.info("🚀 Starting generate career")

        system_prompt = PromptLoader.get_system_prompt()

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
                        "content": f"{self.input_text}",
                    },
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
                presence_penalty=self.presence_penalty,
                frequency_penalty=self.frequency_penalty,
            )
            self.logger.debug(completion.choices[0].message)
            summary = completion.choices[0].message.content.strip()
            self.logger.info("✅ Generation completed")
            return self.fix_truncated_json(summary)

        except Exception as e:
            self.logger.error(f"❌ Generation failed: {str(e)}")
            raise

    def fix_truncated_json(self, truncated_str):
        s = truncated_str.strip()
        
        if s.endswith(','):
            s = s[:-1]
        
        if s.count('{') > s.count('}'):
            last_open = s.rfind('{')
            last_close_after = s.find('}', last_open)
            if last_close_after == -1:
                s = s[:last_open].rstrip()
                if s.endswith(','):
                    s = s[:-1]
        
        if s.count('[') > s.count(']'):
            s += ']'
        
        try:
            return s
        except json.JSONDecodeError as e:
            brace_count = 0
            in_string = False
            escaped = False
            valid_up_to = 0
            
            for i, char in enumerate(s):
                if not escaped:
                    if char == '"':
                        in_string = not in_string
                    elif not in_string:
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                if char == '\\' and not escaped:
                    escaped = True
                else:
                    escaped = False

                if not in_string and brace_count == 0 and s[i:i+1] in [',', ']', '}']:
                    valid_up_to = i + 1

            if valid_up_to > 0:
                candidate = s[:valid_up_to]
                if candidate.count('[') > candidate.count(']'):
                    candidate = candidate.rstrip().rstrip(',')
                    candidate += ']'
                try:
                    return candidate
                except:
                    pass

            return ""