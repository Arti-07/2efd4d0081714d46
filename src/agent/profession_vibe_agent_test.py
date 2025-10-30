import asyncio
import json

from src.agent.core.profession_vibe_agent import ProfessionVibeAgent


async def main():
    """Test profession vibe agent with sample data"""

    # Пример данных теста личности
    personality_data = {
        "code": "ENTP-T",
        "personality_type": "Полемист (Турбулентный)",
        "description": "Креативный мыслитель, постоянно ищущий улучшения.",
        "strengths": "Инновационное мышление, адаптивность, открытость к критике",
        "weaknesses": "Могут быть непостоянны, трудности с фокусировкой",
    }

    # Пример данных астрологии
    astrology_data = {
        "zodiac_sign": "Водолей",
        "element": "Воздух",
        "traits": "Независимый, прогрессивный, гуманитарный",
        "strengths": "Оригинальность, прогрессивность, гуманность",
    }

    # Тестовые профессии
    professions = [
        "Системный администратор",
        "DevOps-инженер",
        "Дизайнер интерфейсов",
        "Маркетинг-менеджер",
        "Психолог",
    ]

    for profession in professions:
        print(f"\n{'='*60}")
        print(f"Тестируем профессию: {profession}")
        print('='*60)
        
        try:
            agent = ProfessionVibeAgent(
                profession_title=profession,
                personality_data=personality_data,
                astrology_data=astrology_data,
                model="Qwen/Qwen3-235B-A22B-Instruct-2507",
                temperature=0.5,
                max_tokens=4096,
            )
            
            questions_data = await agent.generate_questions()
            
            print(f"\n[OK] Сгенерировано вопросов: {len(questions_data['questions'])}")
            print(json.dumps(questions_data, ensure_ascii=False, indent=2))
            
            # Проверка структуры
            for i, q in enumerate(questions_data['questions'], 1):
                print(f"\n{i}. {q.get('question')}")
                print(f"   Вариантов ответа: {len(q.get('options', []))}")
                for opt in q.get('options', []):
                    print(f"   - {opt.get('text')}")
                    
        except Exception as e:
            print(f"\n[ERROR] Ошибка: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

