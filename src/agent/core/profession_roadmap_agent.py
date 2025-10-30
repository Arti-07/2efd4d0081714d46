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
            
            # 🚨 CRITICAL: Ensure interviewQuestions exist in every stage
            roadmap_data = self._ensure_interview_questions(roadmap_data)
            
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
        
        # Fix common text issues that break JSON
        # Replace problematic patterns before JSON parsing
        response = self._sanitize_text_content(response)
        
        # Fix truncated JSON
        return self._fix_truncated_json(response)
    
    def _sanitize_text_content(self, text: str) -> str:
        """Sanitize text content to avoid JSON parsing issues"""
        import re
        
        # Fix unescaped newlines within strings
        text = text.replace('\r\n', ' ').replace('\r', ' ')
        
        # More aggressive backslash fixing
        # First, temporarily mark valid escape sequences
        text = text.replace(r'\"', '\x00QUOTE\x00')
        text = text.replace(r'\\', '\x00BACKSLASH\x00')
        text = text.replace(r'\/', '\x00SLASH\x00')
        text = text.replace(r'\n', '\x00NEWLINE\x00')
        text = text.replace(r'\t', '\x00TAB\x00')
        text = text.replace(r'\r', '\x00RETURN\x00')
        text = text.replace(r'\b', '\x00BACKSPACE\x00')
        text = text.replace(r'\f', '\x00FORMFEED\x00')
        
        # Now escape all remaining backslashes
        text = text.replace('\\', '\\\\')
        
        # Restore valid escape sequences
        text = text.replace('\x00QUOTE\x00', r'\"')
        text = text.replace('\x00BACKSLASH\x00', r'\\')
        text = text.replace('\x00SLASH\x00', r'\/')
        text = text.replace('\x00NEWLINE\x00', r'\n')
        text = text.replace('\x00TAB\x00', r'\t')
        text = text.replace('\x00RETURN\x00', r'\r')
        text = text.replace('\x00BACKSPACE\x00', r'\b')
        text = text.replace('\x00FORMFEED\x00', r'\f')
        
        return text
    
    def _ensure_interview_questions(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure every stage has interviewQuestions field (add fallback if missing)"""
        stages = roadmap_data.get('stages', [])
        
        for i, stage in enumerate(stages):
            if 'interviewQuestions' not in stage or not stage['interviewQuestions']:
                level = stage.get('level', 'UNKNOWN')
                self.logger.warning(f"⚠️ Stage {i+1} ({level}) missing interviewQuestions - adding fallback")
                
                # Add fallback questions based on level
                stage['interviewQuestions'] = self._get_fallback_questions(level, stage.get('title', ''))
        
        return roadmap_data
    
    def _get_fallback_questions(self, level: str, stage_title: str) -> list:
        """Generate fallback interview questions if AI didn't provide them"""
        fallback_questions = {
            'BEGINNER': [
                {
                    "question": "Расскажите о базовых концепциях в этой области",
                    "answer": "Важно понимать фундаментальные принципы и терминологию. Начните с основ и постепенно углубляйтесь в детали."
                },
                {
                    "question": "Какие инструменты вы уже изучили или планируете изучить?",
                    "answer": "На начальном уровне важно освоить базовые инструменты и технологии, которые широко используются в индустрии."
                },
                {
                    "question": "Опишите свой первый проект в этой области",
                    "answer": "Даже простой проект демонстрирует понимание основ. Расскажите о задачах, решениях и что вы узнали в процессе."
                },
            ],
            'JUNIOR': [
                {
                    "question": "Как вы решаете типичные задачи в своей работе?",
                    "answer": "Опишите свой подход к решению проблем, используемые паттерны и методы отладки."
                },
                {
                    "question": "Расскажите о проекте, над которым вы работали",
                    "answer": "Подробно опишите свою роль, технологии, с которыми работали, и результаты проекта."
                },
            ],
            'MIDDLE': [
                {
                    "question": "Как вы проектируете архитектуру решения?",
                    "answer": "Объясните свой подход к архитектурным решениям, учет масштабируемости и поддерживаемости."
                },
                {
                    "question": "Опишите сложную техническую проблему, которую вы решили",
                    "answer": "Расскажите о проблеме, вашем анализе, выборе решения и результатах."
                },
            ],
            'SENIOR': [
                {
                    "question": "Как вы принимаете архитектурные решения для крупных проектов?",
                    "answer": "Опишите процесс анализа требований, выбора технологий и обоснования решений перед командой."
                },
                {
                    "question": "Как вы менторите junior-разработчиков?",
                    "answer": "Расскажите о вашем подходе к обучению, code review и развитию команды."
                },
            ],
            'EXPERT': [
                {
                    "question": "Какие тренды в индустрии вы считаете наиболее важными?",
                    "answer": "Обсудите текущие и будущие тенденции, их влияние на индустрию и ваше видение развития."
                },
                {
                    "question": "Как вы решаете комплексные архитектурные вызовы?",
                    "answer": "Опишите ваш подход к сложным системным решениям, учет trade-offs и долгосрочную стратегию."
                },
            ],
        }
        
        # Return fallback questions for the level
        return fallback_questions.get(level, fallback_questions['BEGINNER'])[:5]

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

