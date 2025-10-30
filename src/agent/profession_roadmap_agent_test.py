import asyncio
import json

from src.agent.core.profession_roadmap_agent import ProfessionRoadmapAgent


async def main():
    """Test profession roadmap agent with complete user profile data"""

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

    # Выбранная профессия
    profession_title = "Backend Python разработчик"

    # Создаем агента со всеми данными
    agent = ProfessionRoadmapAgent(
        profession_title=profession_title,
        personality_data=personality_data,
        astrology_data=astrology_data,
        current_level=None,  # Можно указать "BEGINNER", "JUNIOR", "MIDDLE", "SENIOR", "EXPERT"
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        temperature=0.4,
        top_p=0.9,
        max_tokens=16384,
    )

    try:
        result = await agent.generate_roadmap()
        
        print("\n" + "="*80)
        print("СГЕНЕРИРОВАННЫЙ CAREER ROADMAP")
        print("="*80)
        
        print(f"\n📋 Профессия: {result.get('profession')}")
        
        # Обзор
        overview = result.get('overview', {})
        print(f"\n📖 ОБЗОР")
        print(f"   Описание: {overview.get('description')}")
        print(f"   Общая длительность: {overview.get('totalDuration')}")
        print(f"   Ключевые навыки: {', '.join(overview.get('keySkills', []))}")
        
        if overview.get('personalityInsight'):
            print(f"   💡 Личность: {overview.get('personalityInsight')}")
        
        if overview.get('astrologyInsight'):
            print(f"   ⭐ Астрология: {overview.get('astrologyInsight')}")
        
        # Этапы
        stages = result.get('stages', [])
        print(f"\n🎯 ЭТАПЫ РАЗВИТИЯ ({len(stages)} этапов)")
        for i, stage in enumerate(stages, 1):
            print(f"\n{'-'*80}")
            print(f"ЭТАП {i}: {stage.get('level')} - {stage.get('title')}")
            print(f"{'-'*80}")
            print(f"Длительность: {stage.get('duration')}")
            print(f"Описание: {stage.get('description')}")
            
            print(f"\n  🎯 Цели ({len(stage.get('goals', []))}):")
            for goal in stage.get('goals', [])[:3]:  # Показываем первые 3
                print(f"     • {goal}")
            
            print(f"\n  🔧 Навыки ({len(stage.get('skills', []))}):")
            for skill in stage.get('skills', [])[:3]:  # Показываем первые 3
                print(f"     • {skill.get('name')} ({skill.get('importance')}) - {skill.get('description')}")
            
            print(f"\n  🛠️ Инструменты ({len(stage.get('tools', []))}):")
            for tool in stage.get('tools', [])[:5]:  # Показываем первые 5
                print(f"     • {tool.get('name')} ({tool.get('category')})")
            
            print(f"\n  💬 Вопросы на собеседовании ({len(stage.get('interviewQuestions', []))}):")
            for qa in stage.get('interviewQuestions', [])[:3]:  # Показываем первые 3
                print(f"     Q: {qa.get('question')}")
                print(f"     A: {qa.get('answer')[:100]}...")
        
        # Сохраняем полный результат в JSON файл
        with open("roadmap_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n{'='*80}")
        print("✅ Полный roadmap сохранен в файл: roadmap_result.json")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
