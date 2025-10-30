import sqlite3
import uuid
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.database.db import get_db_connection


def save_roadmap(user_id: str, profession_title: str, roadmap_data: Dict[str, Any]) -> str:
    """
    Сохранить roadmap для пользователя
    Если roadmap для этой профессии уже существует - обновляет его
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Проверяем есть ли уже roadmap для этой профессии
        cursor.execute("""
            SELECT id FROM roadmaps 
            WHERE user_id = ? AND profession_title = ?
        """, (user_id, profession_title))
        
        existing = cursor.fetchone()
        
        if existing:
            # Обновляем существующий
            roadmap_id = existing['id']
            cursor.execute("""
                UPDATE roadmaps 
                SET roadmap_data = ?, updated_at = ?
                WHERE id = ?
            """, (
                json.dumps(roadmap_data, ensure_ascii=False),
                datetime.now().isoformat(),
                roadmap_id
            ))
        else:
            # Создаем новый
            roadmap_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO roadmaps (id, user_id, profession_title, roadmap_data)
                VALUES (?, ?, ?, ?)
            """, (
                roadmap_id,
                user_id,
                profession_title,
                json.dumps(roadmap_data, ensure_ascii=False)
            ))
        
        conn.commit()
        return roadmap_id


def get_roadmap(user_id: str, profession_title: str) -> Optional[Dict[str, Any]]:
    """
    Получить roadmap пользователя для конкретной профессии
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, profession_title, roadmap_data, created_at, updated_at
            FROM roadmaps 
            WHERE user_id = ? AND profession_title = ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (user_id, profession_title))
        
        row = cursor.fetchone()
        
        if row:
            return {
                'id': row['id'],
                'profession_title': row['profession_title'],
                'roadmap': json.loads(row['roadmap_data']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
        
        return None


def get_user_roadmaps(user_id: str) -> List[Dict[str, Any]]:
    """
    Получить все roadmaps пользователя
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, profession_title, roadmap_data, created_at, updated_at
            FROM roadmaps 
            WHERE user_id = ?
            ORDER BY updated_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        
        return [
            {
                'id': row['id'],
                'profession_title': row['profession_title'],
                'roadmap': json.loads(row['roadmap_data']),
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }
            for row in rows
        ]


def delete_roadmap(roadmap_id: str, user_id: str) -> bool:
    """
    Удалить roadmap (с проверкой что он принадлежит пользователю)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM roadmaps 
            WHERE id = ? AND user_id = ?
        """, (roadmap_id, user_id))
        
        conn.commit()
        return cursor.rowcount > 0

