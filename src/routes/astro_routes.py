from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.models.astro_model import BirthDataInput, AstroProfile
from src.utils.astrology import create_astro_profile
from src.utils.auth import verify_token
from src.database.db import get_user_by_username
from src.database.astro_db import save_astro_profile, get_astro_profile, delete_astro_profile

router = APIRouter(prefix="/astrology", tags=["Astrology"])
security = HTTPBearer()


@router.post("/profile", response_model=AstroProfile)
async def create_or_update_astro_profile(
    birth_data: BirthDataInput,
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
    
    try:
        profile_data = create_astro_profile(
            birth_data.birth_date,
            birth_data.birth_time,
            birth_data.birth_city,
            birth_data.birth_country
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    saved_profile = save_astro_profile(user["id"], profile_data)
    
    return AstroProfile(
        user_id=saved_profile["user_id"],
        birth_date=saved_profile["birth_date"],
        birth_time=saved_profile["birth_time"],
        birth_city=saved_profile["birth_city"],
        birth_country=saved_profile["birth_country"],
        zodiac_sign=saved_profile["zodiac_sign"],
        zodiac_element=saved_profile["zodiac_element"],
        zodiac_quality=saved_profile["zodiac_quality"],
        chinese_zodiac=saved_profile["chinese_zodiac"],
        life_path_number=saved_profile["life_path_number"],
        soul_number=saved_profile["soul_number"],
        personality_traits=saved_profile["personality_traits"],
        career_recommendations=saved_profile["career_recommendations"],
        strengths=saved_profile["strengths"],
        challenges=saved_profile["challenges"],
        compatibility_signs=saved_profile["compatibility_signs"],
        created_at=saved_profile["created_at"],
        updated_at=saved_profile["updated_at"]
    )


@router.get("/profile", response_model=AstroProfile)
async def get_my_astro_profile(
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
    
    profile = get_astro_profile(user["id"])
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Астрологический профиль не найден. Создайте его сначала."
        )
    
    return AstroProfile(
        user_id=profile["user_id"],
        birth_date=profile["birth_date"],
        birth_time=profile["birth_time"],
        birth_city=profile["birth_city"],
        birth_country=profile["birth_country"],
        zodiac_sign=profile["zodiac_sign"],
        zodiac_element=profile["zodiac_element"],
        zodiac_quality=profile["zodiac_quality"],
        chinese_zodiac=profile["chinese_zodiac"],
        life_path_number=profile["life_path_number"],
        soul_number=profile["soul_number"],
        personality_traits=profile["personality_traits"],
        career_recommendations=profile["career_recommendations"],
        strengths=profile["strengths"],
        challenges=profile["challenges"],
        compatibility_signs=profile["compatibility_signs"],
        created_at=profile["created_at"],
        updated_at=profile["updated_at"]
    )


@router.delete("/profile")
async def delete_my_astro_profile(
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
    
    deleted = delete_astro_profile(user["id"])
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Астрологический профиль не найден"
        )
    
    return {"message": "Астрологический профиль успешно удален"}

