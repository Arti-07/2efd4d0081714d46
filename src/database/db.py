from __future__ import annotations

import sqlite3
import uuid
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from src.config import settings


def init_database():
    db_path = Path(settings.DATABASE_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_username 
        ON users(username)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personality_results (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            personality_type TEXT NOT NULL,
            code TEXT NOT NULL,
            mind_score INTEGER NOT NULL,
            energy_score INTEGER NOT NULL,
            nature_score INTEGER NOT NULL,
            tactics_score INTEGER NOT NULL,
            identity_score INTEGER NOT NULL,
            description TEXT NOT NULL,
            full_description TEXT NOT NULL,
            strengths TEXT NOT NULL,
            weaknesses TEXT NOT NULL,
            career_advice TEXT NOT NULL,
            careers TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_personality_user_id 
        ON personality_results(user_id)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS astro_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT UNIQUE NOT NULL,
            birth_date TEXT NOT NULL,
            birth_time TEXT,
            birth_city TEXT,
            birth_country TEXT,
            zodiac_sign TEXT NOT NULL,
            zodiac_element TEXT NOT NULL,
            zodiac_quality TEXT NOT NULL,
            chinese_zodiac TEXT NOT NULL,
            life_path_number INTEGER NOT NULL,
            soul_number INTEGER,
            personality_traits TEXT NOT NULL,
            career_recommendations TEXT NOT NULL,
            strengths TEXT NOT NULL,
            challenges TEXT NOT NULL,
            compatibility_signs TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_astro_user_id 
        ON astro_profiles(user_id)
    """)

    # Таблица для roadmaps
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roadmaps (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            profession_title TEXT NOT NULL,
            roadmap_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_roadmaps_user_id 
        ON roadmaps(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_roadmaps_user_profession 
        ON roadmaps(user_id, profession_title)
    """)

    conn.commit()
    conn.close()

    print(f"✅ База данных инициализирована: {settings.DATABASE_PATH}")


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def get_user_by_username(username: str) -> dict | None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, hashed_password, created_at FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()

        if row:
            return {
                "id": row["id"],
                "username": row["username"],
                "hashed_password": row["hashed_password"],
                "created_at": row["created_at"]
            }
        return None


def get_user_by_id(user_id: str) -> dict | None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, created_at FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()

        if row:
            return {
                "id": row["id"],
                "username": row["username"],
                "created_at": row["created_at"]
            }
        return None


def create_user(username: str, hashed_password: str) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        user_id = str(uuid.uuid4())
        cursor.execute(
            "INSERT INTO users (id, username, hashed_password) VALUES (?, ?, ?)",
            (user_id, username, hashed_password)
        )
        conn.commit()

        return {
            "id": user_id,
            "username": username,
            "created_at": datetime.now().isoformat()
        }


def user_exists(username: str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None
