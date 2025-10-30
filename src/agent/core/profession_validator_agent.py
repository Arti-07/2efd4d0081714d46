# profession_validator_agent.py
import logging
import uuid
import json
import httpx
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


class ProfessionValidatorAgent:
    """Agent that validates profession existence using HH.ru API and AI analysis"""

    name: str = "profession_validator_agent"

    def __init__(
        self,
        profession_title: str,
        model: str = "Qwen/Qwen3-235B-A22B-Instruct-2507",
        max_tokens: Optional[int] = 2048,
        temperature: float = 0.3,
        top_p: float = 0.9,
    ):
        self.id = f"{self.name}_{uuid.uuid4()}"
        self.logger = logging.getLogger(self.id)
        
        self.profession_title = profession_title.strip()
        
        self.model = config.model_name if config.model_name else model
        self.max_tokens = max_tokens
        self.temperature = temperature 
        self.top_p = top_p

        client_kwargs = {"base_url": config.base_url.strip(), "api_key": config.api_key}
        self.openai_client = AsyncOpenAI(**client_kwargs)

    async def validate_profession(self) -> Dict[str, Any]:
        """
        Validate profession by checking HH.ru API and using AI to analyze results.
        Returns validation result with status and suggestions.
        """
        self.logger.info(f"🔍 Validating profession: {self.profession_title}")

        # Step 1: Search HH.ru API
        hh_results = await self._search_hh_api()
        
        # Step 2: Analyze results with AI
        validation_result = await self._analyze_with_ai(hh_results)
        
        return validation_result

    async def _search_hh_api(self) -> Dict[str, Any]:
        """Search HH.ru API for vacancies matching the profession"""
        try:
            async with httpx.AsyncClient() as client:
                # HH.ru API endpoint for vacancy search
                url = "https://api.hh.ru/vacancies"
                # Build params for HH.ru API
                # Note: HH.ru API may not accept quotes in text parameter via GET request
                params = {
                    "text": self.profession_title,  # Search query
                    "per_page": 20,  # Get top 20 results
                    "page": 0,  # First page
                    # Area 113 = Russia, but we'll omit it to search globally
                }
                
                # Use browser-like headers to avoid blocking
                headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'accept-language': 'ru,en;q=0.9',
                    'cache-control': 'max-age=0',
                    'priority': 'u=0, i',
                    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "YaBrowser";v="25.8", "Yowser";v="2.5"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'document',
                    'sec-fetch-mode': 'navigate',
                    'sec-fetch-site': 'none',
                    'sec-fetch-user': '?1',
                    'upgrade-insecure-requests': '1',
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 YaBrowser/25.8.0.0 Safari/537.36'
                }
                
                response = await client.get(url, params=params, headers=headers, timeout=10.0)
                response.raise_for_status()
                
                data = response.json()
                
                self.logger.info(f"✅ HH.ru API: Found {data.get('found', 0)} vacancies")
                
                return {
                    "success": True,
                    "total_found": data.get("found", 0),
                    "vacancies": data.get("items", []),
                    "query": self.profession_title,
                }
                
        except httpx.HTTPStatusError as e:
            error_detail = f"{str(e)}"
            try:
                # Try to get error details from response
                error_body = e.response.text
                self.logger.error(f"❌ HH.ru API error: {error_detail}\nResponse: {error_body}")
            except:
                self.logger.error(f"❌ HH.ru API error: {error_detail}")
            
            return {
                "success": False,
                "error": str(e),
                "total_found": 0,
                "vacancies": [],
                "query": self.profession_title,
            }
        except httpx.HTTPError as e:
            self.logger.error(f"❌ HH.ru HTTP error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_found": 0,
                "vacancies": [],
                "query": self.profession_title,
            }
        except Exception as e:
            self.logger.error(f"❌ Unexpected error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "total_found": 0,
                "vacancies": [],
                "query": self.profession_title,
            }

    async def _analyze_with_ai(self, hh_results: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to analyze HH.ru results and determine if profession is valid"""
        
        # Load system prompt from file
        system_prompt = PromptLoader.get_prompt("profession_validator_prompt.txt")

        # Prepare vacancy data for analysis - extract actual job titles
        vacancies = hh_results.get("vacancies", [])[:10]
        vacancy_names = [v.get("name", "") for v in vacancies]
        
        # Format vacancy list for better readability
        vacancy_list = "\n".join([f"  {i+1}. {name}" for i, name in enumerate(vacancy_names) if name])
        
        user_content = f"""Проанализируй профессию: "{self.profession_title}"

Результаты поиска на HH.ru:
- Всего найдено результатов: {hh_results.get('total_found', 0)}
- Реальные названия вакансий (поле "name" из API):
{vacancy_list if vacancy_list else "  (нет вакансий)"}

ВАЖНО: 
1. Проверь, встречается ли запрошенная профессия в реальных названиях должностей
2. Если слово есть только в описании как метафора (например, "стань волшебником продаж") - профессия НЕВАЛИДНА
3. Для валидной профессии названия вакансий должны содержать саму профессию или близкие варианты

Определи валидность профессии и дай рекомендацию."""

        try:
            completion = await self.openai_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": config.http_referer,
                    "X-Title": config.x_title,
                },
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=self.top_p,
            )
            
            response_content = completion.choices[0].message.content.strip()
            self.logger.debug(f"AI response: {response_content}")
            
            # Clean and parse JSON
            cleaned_json = self._clean_json_response(response_content)
            result = json.loads(cleaned_json)
            
            # Add HH.ru data to result
            result["hh_total_found"] = hh_results.get("total_found", 0)
            result["query"] = self.profession_title
            
            self.logger.info(f"✅ Validation result: {result.get('status')}")
            return result

        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parsing failed: {str(e)}")
            # Fallback response
            return self._create_fallback_response(hh_results)
        except Exception as e:
            self.logger.error(f"❌ AI analysis failed: {str(e)}")
            return self._create_fallback_response(hh_results)

    def _clean_json_response(self, response: str) -> str:
        """Clean response to extract valid JSON"""
        # Remove markdown code blocks if present
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        return response.strip()

    def _create_fallback_response(self, hh_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback validation response based on HH.ru results count"""
        total_found = hh_results.get("total_found", 0)
        
        if total_found == 0:
            return {
                "is_valid": False,
                "status": "invalid",
                "message": f'К сожалению, профессия "{self.profession_title}" не найдена на рынке труда. Возможно, это устаревшая или фантастическая профессия. Пожалуйста, выберите другую профессию.',
                "suggestions": [],
                "found_count": 0,
                "sample_vacancies": [],
                "hh_total_found": 0,
                "query": self.profession_title,
            }
        elif total_found < 5:
            vacancy_names = [v.get("name", "") for v in hh_results.get("vacancies", [])[:3]]
            return {
                "is_valid": True,
                "status": "rare",
                "message": f'Профессия "{self.profession_title}" редко встречается на рынке (найдено {total_found} вакансий). Вы можете продолжить или выбрать более распространенную профессию.',
                "suggestions": [],
                "found_count": total_found,
                "sample_vacancies": vacancy_names,
                "hh_total_found": total_found,
                "query": self.profession_title,
            }
        else:
            vacancy_names = [v.get("name", "") for v in hh_results.get("vacancies", [])[:5]]
            return {
                "is_valid": True,
                "status": "valid",
                "message": f'Профессия "{self.profession_title}" подтверждена! Найдено {total_found} вакансий на рынке труда.',
                "suggestions": [],
                "found_count": total_found,
                "sample_vacancies": vacancy_names,
                "hh_total_found": total_found,
                "query": self.profession_title,
            }

