"""
Простой пример использования ProfessionAmbientsAgent

Этот агент генерирует иммерсивные окружения (ambients) для выбранной профессии,
включая:
- Текстовые описания ситуаций
- Промпты для генерации изображений
- Промпты для генерации звуков
- Голосовые фразы
- Список инструментов профессии с эмодзи
"""

import asyncio
import json
from src.agent.core.profession_ambients_agent import ProfessionAmbientsAgent


async def generate_simple_example():
    """Простой пример с минимальным набором данных"""
    
    agent = ProfessionAmbientsAgent(
        profession_title="UX/UI Дизайнер",
        personality_data={
            "code": "INFP",
            "personality_type": "Медиатор",
            "strengths": "Креативность, эмпатия, внимание к деталям"
        },
        clarifying_data={
            "questions": [
                {
                    "question": "Какой тип проектов вам интересен?",
                    "answer": "Мобильные приложения"
                }
            ]
        }
    )
    
    result = await agent.generate_ambients()
    
    print("\n" + "="*60)
    print(f"Профессия: {result['profession_title']}")
    print(f"Окружений: {len(result['ambients'])}")
    print("="*60)
    
    # Выводим каждое окружение
    for ambient in result['ambients']:
        print(f"\n{ambient['name']}:")
        print(f"  {ambient['text'][:100]}...")
        if ambient.get('image_prompt'):
            print(f"  [Есть промпт для изображения]")
        if ambient.get('sound_prompt'):
            print(f"  [Есть промпт для звуков]")
        if ambient.get('voice'):
            print(f"  Голос: \"{ambient['voice']}\"")
    
    print(f"\n{result['tools']['title']}:")
    print(f"  Всего инструментов: {len(result['tools']['items'])}")
    
    return result


if __name__ == "__main__":
    result = asyncio.run(generate_simple_example())
    
    # Сохраняем для просмотра
    with open("simple_example_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\nРезультат сохранен в simple_example_result.json")

