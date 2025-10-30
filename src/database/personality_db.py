from __future__ import annotations

import uuid
import json
from datetime import datetime
from src.database.db import get_db_connection


def save_personality_result(user_id: str, result: dict) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        result_id = str(uuid.uuid4())
        cursor.execute(
            """INSERT INTO personality_results 
            (id, user_id, personality_type, code, mind_score, energy_score, 
             nature_score, tactics_score, identity_score, description, 
             full_description, strengths, weaknesses, career_advice, careers) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                result_id,
                user_id,
                result["personality_type"],
                result["code"],
                result["mind_score"],
                result["energy_score"],
                result["nature_score"],
                result["tactics_score"],
                result["identity_score"],
                result["description"],
                result["full_description"],
                result["strengths"],
                result["weaknesses"],
                result["career_advice"],
                json.dumps(result["careers"])
            )
        )
        conn.commit()

        return {
            "id": result_id,
            "user_id": user_id,
            **result,
            "created_at": datetime.now().isoformat()
        }


def get_user_personality_results(user_id: str) -> list:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, personality_type, code, mind_score, energy_score,
                      nature_score, tactics_score, identity_score, description,
                      full_description, strengths, weaknesses, career_advice, 
                      careers, created_at 
               FROM personality_results 
               WHERE user_id = ? 
               ORDER BY created_at DESC""",
            (user_id,)
        )
        rows = cursor.fetchall()

        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "personality_type": row["personality_type"],
                "code": row["code"],
                "mind_score": row["mind_score"],
                "energy_score": row["energy_score"],
                "nature_score": row["nature_score"],
                "tactics_score": row["tactics_score"],
                "identity_score": row["identity_score"],
                "description": row["description"],
                "full_description": row["full_description"],
                "strengths": row["strengths"],
                "weaknesses": row["weaknesses"],
                "career_advice": row["career_advice"],
                "careers": json.loads(row["careers"]),
                "created_at": row["created_at"]
            })

        return results


def get_latest_personality_result(user_id: str) -> dict | None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, personality_type, code, mind_score, energy_score,
                      nature_score, tactics_score, identity_score, description,
                      full_description, strengths, weaknesses, career_advice, 
                      careers, created_at 
               FROM personality_results 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT 1""",
            (user_id,)
        )
        row = cursor.fetchone()

        if row:
            return {
                "id": row["id"],
                "user_id": user_id,
                "personality_type": row["personality_type"],
                "code": row["code"],
                "mind_score": row["mind_score"],
                "energy_score": row["energy_score"],
                "nature_score": row["nature_score"],
                "tactics_score": row["tactics_score"],
                "identity_score": row["identity_score"],
                "description": row["description"],
                "full_description": row["full_description"],
                "strengths": row["strengths"],
                "weaknesses": row["weaknesses"],
                "career_advice": row["career_advice"],
                "careers": json.loads(row["careers"]),
                "created_at": row["created_at"]
            }
        return None


def delete_personality_result(user_id: str, result_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM personality_results WHERE user_id = ? AND id = ?",
            (user_id, result_id)
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_all_personality_results(user_id: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM personality_results WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
