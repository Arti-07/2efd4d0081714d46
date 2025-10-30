from __future__ import annotations

import uuid
import json
from datetime import datetime
from src.database.db import get_db_connection


def save_astro_profile(user_id: str, profile_data: dict) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM astro_profiles WHERE user_id = ?", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute(
                """UPDATE astro_profiles 
                SET birth_date = ?, birth_time = ?, birth_city = ?, birth_country = ?,
                    zodiac_sign = ?, zodiac_element = ?, zodiac_quality = ?,
                    chinese_zodiac = ?, life_path_number = ?, soul_number = ?,
                    personality_traits = ?, career_recommendations = ?,
                    strengths = ?, challenges = ?, compatibility_signs = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?""",
                (
                    profile_data["birth_date"],
                    profile_data["birth_time"],
                    profile_data["birth_city"],
                    profile_data["birth_country"],
                    profile_data["zodiac_sign"],
                    profile_data["zodiac_element"],
                    profile_data["zodiac_quality"],
                    profile_data["chinese_zodiac"],
                    profile_data["life_path_number"],
                    profile_data["soul_number"],
                    profile_data["personality_traits"],
                    profile_data["career_recommendations"],
                    profile_data["strengths"],
                    profile_data["challenges"],
                    json.dumps(profile_data["compatibility_signs"]),
                    user_id
                )
            )
            profile_id = existing["id"]
        else:
            profile_id = str(uuid.uuid4())
            cursor.execute(
                """INSERT INTO astro_profiles 
                (id, user_id, birth_date, birth_time, birth_city, birth_country,
                 zodiac_sign, zodiac_element, zodiac_quality, chinese_zodiac,
                 life_path_number, soul_number, personality_traits, career_recommendations,
                 strengths, challenges, compatibility_signs) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    profile_id,
                    user_id,
                    profile_data["birth_date"],
                    profile_data["birth_time"],
                    profile_data["birth_city"],
                    profile_data["birth_country"],
                    profile_data["zodiac_sign"],
                    profile_data["zodiac_element"],
                    profile_data["zodiac_quality"],
                    profile_data["chinese_zodiac"],
                    profile_data["life_path_number"],
                    profile_data["soul_number"],
                    profile_data["personality_traits"],
                    profile_data["career_recommendations"],
                    profile_data["strengths"],
                    profile_data["challenges"],
                    json.dumps(profile_data["compatibility_signs"])
                )
            )
        
        conn.commit()
        
        return {
            "id": profile_id,
            "user_id": user_id,
            **profile_data,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }


def get_astro_profile(user_id: str) -> dict | None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, birth_date, birth_time, birth_city, birth_country,
                      zodiac_sign, zodiac_element, zodiac_quality, chinese_zodiac,
                      life_path_number, soul_number, personality_traits,
                      career_recommendations, strengths, challenges,
                      compatibility_signs, created_at, updated_at
               FROM astro_profiles 
               WHERE user_id = ?""",
            (user_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row["id"],
                "user_id": user_id,
                "birth_date": row["birth_date"],
                "birth_time": row["birth_time"],
                "birth_city": row["birth_city"],
                "birth_country": row["birth_country"],
                "zodiac_sign": row["zodiac_sign"],
                "zodiac_element": row["zodiac_element"],
                "zodiac_quality": row["zodiac_quality"],
                "chinese_zodiac": row["chinese_zodiac"],
                "life_path_number": row["life_path_number"],
                "soul_number": row["soul_number"],
                "personality_traits": row["personality_traits"],
                "career_recommendations": row["career_recommendations"],
                "strengths": row["strengths"],
                "challenges": row["challenges"],
                "compatibility_signs": json.loads(row["compatibility_signs"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        return None


def delete_astro_profile(user_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM astro_profiles WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0

