import asyncio
import json

from src.agent.core.profession_cards_agent import ProfessionCardsAgent


async def main():
    """Test profession cards agent with sample personality and astrology data"""

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

    # Создаем агента с обоими типами данных
    agent = ProfessionCardsAgent(
        personality_data=personality_data,
        astrology_data=astrology_data,
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        temperature=0.4,
        top_p=0.9,
        max_tokens=8192,
    )

    try:
        cards = await agent.generate_profession_cards()
        print("\n✨ Сгенерированные карточки профессий:")
        print(json.dumps(cards, ensure_ascii=False, indent=2))
        print(f"\n📊 Всего карточек: {len(cards)}")
        
        # Проверка структуры
        for i, card in enumerate(cards, 1):
            print(f"\n{i}. {card.get('title')} ({card.get('matchScore')}%)")
            print(f"   Иконка: {card.get('icon')}")
            print(f"   На основе: {', '.join(card.get('basedOn', []))}")
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())

