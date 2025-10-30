import asyncio
import json

from src.agent.core.profession_ambients_agent import ProfessionAmbientsAgent


async def main():
    """Test profession ambients agent with complete user profile data"""

    # Пример данных теста личности
    personality_data = {
        "code": "ENTP-T",
        "personality_type": "Полемист (Турбулентный)",
        "description": "Креативный мыслитель, постоянно ищущий улучшения.",
        "full_description": "Турбулентные Полемисты сочетают интеллектуальное любопытство с желанием постоянно совершенствоваться. Они более осторожны в споре и чувствительны к реакциям других. Открыты к обратной связи и готовы пересматривать свои идеи.",
        "strengths": "Инновационное мышление, адаптивность, открытость к критике, креативность, энергичность",
        "weaknesses": "Могут быть непостоянны, трудности с фокусировкой, чувствительность к неудачам",
        "career_advice": "Подходят динамичные роли, где ценится креативность и гибкость мышления. Рекомендуется работать с менторами или в командах, которые помогут направить энергию. Развивайте дисциплину завершения проектов.",
        "careers": ["Инноватор", "Креативный директор", "Консультант", "Продакт-менеджер", "Предприниматель"]
    }

    # Пример данных астрологии
    astrology_data = {
        "zodiac_sign": "Водолей",
        "element": "Воздух",
        "quality": "Фиксированный",
        "traits": "Независимый, прогрессивный, гуманитарный. Оригинальный мыслитель и реформатор.",
        "careers": ["Изобретатель", "Программист", "Ученый", "Активист", "Астролог"],
        "strengths": "Оригинальность, прогрессивность, гуманность, интеллект, независимость",
        "challenges": "Отстраненность, упрямство, непредсказуемость, холодность"
    }

    # Пример выбранной профессии
    profession_title = "Программист"

    # Пример данных с уточняющими вопросами и ответами
    clarifying_data = {
        "questions": [
            {
                "id": "q1",
                "question": "Какой у вас уровень опыта в программировании?",
                "answer": "Middle - 2-4 года опыта, могу самостоятельно решать большинство задач"
            },
            {
                "id": "q2",
                "question": "В какой компании вы хотели бы работать?",
                "answer": "Средний бизнес - растущая компания с устоявшимися процессами"
            },
            {
                "id": "q3",
                "question": "Какой стек технологий вам ближе?",
                "answer": "Backend - работа с серверной логикой, базами данных, API"
            }
        ]
    }

    # Создаем агента со всеми данными
    agent = ProfessionAmbientsAgent(
        profession_title=profession_title,
        personality_data=personality_data,
        astrology_data=astrology_data,
        clarifying_data=clarifying_data,
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        temperature=0.6,
        top_p=0.9,
        max_tokens=8192,
    )

    try:
        result = await agent.generate_ambients()
        
        print("\n" + "="*80)
        print("СГЕНЕРИРОВАННЫЕ ОКРУЖЕНИЯ ПРОФЕССИИ")
        print("="*80)
        print(f"\nПрофессия: {result.get('profession_title')}")
        print(f"Всего окружений: {len(result.get('ambients', []))}")
        
        # Выводим каждое окружение
        for i, ambient in enumerate(result.get("ambients", []), 1):
            print(f"\n{'-'*80}")
            print(f"ОКРУЖЕНИЕ #{i}: {ambient.get('name')}")
            print(f"{'-'*80}")
            
            if ambient.get("text"):
                print(f"\nОписание:")
                print(f"   {ambient.get('text')}")
            
            if ambient.get("image_prompt"):
                print(f"\nПромпт для изображения:")
                print(f"   {ambient.get('image_prompt')}")
            
            if ambient.get("sound_prompt"):
                print(f"\nПромпт для звуков:")
                print(f"   {ambient.get('sound_prompt')}")
            
            if ambient.get("voice"):
                print(f"\nГолос:")
                print(f"   \"{ambient.get('voice')}\"")
        
        # Сохраняем полный результат в JSON файл СНАЧАЛА
        with open("ambients_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Выводим инструменты
        tools = result.get("tools", {})
        print(f"\n{'='*80}")
        print(f"{tools.get('title', 'ИНСТРУМЕНТЫ ПРОФЕССИИ')}")
        print(f"{'='*80}")
        print(f"Инструментов: {len(tools.get('items', []))}")
        
        print(f"\n{'='*80}\n")
        print("Полный результат сохранен в файл: ambients_result.json")
        
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

