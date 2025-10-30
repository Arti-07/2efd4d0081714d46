from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PersonalityQuestion(BaseModel):
    id: int
    question: str
    dimension: str
    reverse: bool


class QuestionResponse(BaseModel):
    question_id: int
    answer: int


class PersonalityTestSubmission(BaseModel):
    answers: List[QuestionResponse]


class PersonalityResult(BaseModel):
    id: str
    user_id: str
    personality_type: str
    code: str
    mind_score: int
    energy_score: int
    nature_score: int
    tactics_score: int
    identity_score: int
    description: str
    full_description: str
    strengths: str
    weaknesses: str
    career_advice: str
    careers: List[str]
    created_at: str


class PersonalityTestResponse(BaseModel):
    questions: List[PersonalityQuestion]
    total_questions: int

