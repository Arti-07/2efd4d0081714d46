from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

from src.models.personality_model import (
    PersonalityTestResponse,
    PersonalityTestSubmission,
    PersonalityResult,
    PersonalityQuestion
)
from src.utils.personality_test import PERSONALITY_QUESTIONS, calculate_personality_type
from src.utils.auth import verify_token
from src.database.db import get_user_by_username
from src.database.personality_db import (
    save_personality_result,
    get_user_personality_results,
    get_latest_personality_result,
    delete_personality_result,
    delete_all_personality_results
)

router = APIRouter(prefix="/personality", tags=["Personality Test"])
security = HTTPBearer()


@router.get("/questions", response_model=PersonalityTestResponse)
async def get_personality_questions():
    questions = [
        PersonalityQuestion(
            id=q["id"],
            question=q["question"],
            dimension=q["dimension"],
            reverse=q["reverse"]
        )
        for q in PERSONALITY_QUESTIONS
    ]
    
    return PersonalityTestResponse(
        questions=questions,
        total_questions=len(questions)
    )


@router.post("/submit", response_model=PersonalityResult)
async def submit_personality_test(
    submission: PersonalityTestSubmission,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    if len(submission.answers) != len(PERSONALITY_QUESTIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Необходимо ответить на все {len(PERSONALITY_QUESTIONS)} вопросов"
        )
    
    answers_dict = {answer.question_id: answer.answer for answer in submission.answers}
    
    for answer in submission.answers:
        if answer.answer < 1 or answer.answer > 7:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ответы должны быть в диапазоне от 1 до 7"
            )
    
    result = calculate_personality_type(answers_dict)
    
    saved_result = save_personality_result(user["id"], result)
    
    return PersonalityResult(
        id=saved_result["id"],
        user_id=saved_result["user_id"],
        personality_type=saved_result["personality_type"],
        code=saved_result["code"],
        mind_score=saved_result["mind_score"],
        energy_score=saved_result["energy_score"],
        nature_score=saved_result["nature_score"],
        tactics_score=saved_result["tactics_score"],
        identity_score=saved_result["identity_score"],
        description=saved_result["description"],
        full_description=saved_result["full_description"],
        strengths=saved_result["strengths"],
        weaknesses=saved_result["weaknesses"],
        career_advice=saved_result["career_advice"],
        careers=saved_result["careers"],
        created_at=saved_result["created_at"]
    )


@router.get("/results", response_model=List[PersonalityResult])
async def get_my_personality_results(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    results = get_user_personality_results(user["id"])
    
    return [
        PersonalityResult(
            id=r["id"],
            user_id=user["id"],
            personality_type=r["personality_type"],
            code=r["code"],
            mind_score=r["mind_score"],
            energy_score=r["energy_score"],
            nature_score=r["nature_score"],
            tactics_score=r["tactics_score"],
            identity_score=r["identity_score"],
            description=r["description"],
            full_description=r["full_description"],
            strengths=r["strengths"],
            weaknesses=r["weaknesses"],
            career_advice=r["career_advice"],
            careers=r["careers"],
            created_at=r["created_at"]
        )
        for r in results
    ]


@router.get("/latest", response_model=PersonalityResult)
async def get_latest_result(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    result = get_latest_personality_result(user["id"])
    
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результаты теста не найдены. Пройдите тест сначала."
        )
    
    return PersonalityResult(
        id=result["id"],
        user_id=result["user_id"],
        personality_type=result["personality_type"],
        code=result["code"],
        mind_score=result["mind_score"],
        energy_score=result["energy_score"],
        nature_score=result["nature_score"],
        tactics_score=result["tactics_score"],
        identity_score=result["identity_score"],
        description=result["description"],
        full_description=result["full_description"],
        strengths=result["strengths"],
        weaknesses=result["weaknesses"],
        career_advice=result["career_advice"],
        careers=result["careers"],
        created_at=result["created_at"]
    )


@router.delete("/result/{result_id}")
async def delete_test_result(
    result_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    deleted = delete_personality_result(user["id"], result_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результат теста не найден"
        )
    
    return {"message": "Результат теста успешно удален"}


@router.delete("/results")
async def delete_all_test_results(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    username = verify_token(token)
    
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    deleted = delete_all_personality_results(user["id"])
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Результаты тестов не найдены"
        )
    
    return {"message": "Все результаты тестов успешно удалены"}

