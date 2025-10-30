import asyncio

from core.career_navigator_agent import CareerNavigatorAgent

async def main():

    test_input = """
    Искусственный интеллект — это область компьютерных наук, посвящённая созданию систем,
    способных выполнять задачи, которые традиционно требуют человеческого интеллекта.
    К таким задачам относятся распознавание речи, принятие решений, перевод текстов,
    визуальное восприятие и обучение на основе опыта. Современные достижения в области
    глубокого обучения и нейронных сетей позволили ИИ достичь впечатляющих результатов
    в таких сферах, как медицина, финансы, транспорт и развлечения.
    """

    agent = CareerNavigatorAgent(
        input_text=test_input.strip(),
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        temperature=0.3,
        top_p=0.9,
        max_tokens=128,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )

    try:
        career = await agent.createCareer()
        print("\n📝 Карьерный путь:")
        print(career)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    asyncio.run(main())

