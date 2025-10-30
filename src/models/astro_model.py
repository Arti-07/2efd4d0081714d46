from pydantic import BaseModel
from typing import Optional
from datetime import date, time


class BirthDataInput(BaseModel):
    birth_date: str
    birth_time: Optional[str] = None
    birth_city: Optional[str] = None
    birth_country: Optional[str] = None


class AstroProfile(BaseModel):
    user_id: str
    birth_date: str
    birth_time: Optional[str]
    birth_city: Optional[str]
    birth_country: Optional[str]
    zodiac_sign: str
    zodiac_element: str
    zodiac_quality: str
    chinese_zodiac: str
    life_path_number: int
    soul_number: Optional[int]
    personality_traits: str
    career_recommendations: str
    strengths: str
    challenges: str
    compatibility_signs: list[str]
    created_at: str
    updated_at: str


class AstroProfileResponse(BaseModel):
    user_id: str
    birth_date: str
    zodiac_sign: str
    zodiac_element: str
    chinese_zodiac: str
    life_path_number: int
    personality_traits: str
    career_recommendations: str
    created_at: str

