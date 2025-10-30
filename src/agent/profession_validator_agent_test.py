import asyncio
import json

from src.agent.core.profession_validator_agent import ProfessionValidatorAgent


async def test_valid_profession():
    """Тест валидной профессии"""
    print("\n=== Тест 1: Валидная профессия (Python разработчик) ===")
    
    agent = ProfessionValidatorAgent(
        profession_title="Python разработчик",
        temperature=0.3,
        max_tokens=2048,
    )
    
    result = await agent.validate_profession()
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def test_invalid_profession():
    """Тест невалидной/фантастической профессии"""
    print("\n=== Тест 2: Невалидная профессия (Маг) ===")
    
    agent = ProfessionValidatorAgent(
        profession_title="Маг",
        temperature=0.3,
        max_tokens=2048,
    )
    
    result = await agent.validate_profession()
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def test_rare_profession():
    """Тест редкой профессии"""
    print("\n=== Тест 3: Редкая профессия (Космобиолог) ===")
    
    agent = ProfessionValidatorAgent(
        profession_title="Космобиолог",
        temperature=0.3,
        max_tokens=2048,
    )
    
    result = await agent.validate_profession()
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def test_general_profession():
    """Тест слишком общей профессии"""
    print("\n=== Тест 4: Слишком общая профессия (Специалист) ===")
    
    agent = ProfessionValidatorAgent(
        profession_title="Специалист",
        temperature=0.3,
        max_tokens=2048,
    )
    
    result = await agent.validate_profession()
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def test_popular_profession():
    """Тест популярной профессии"""
    print("\n=== Тест 5: Популярная профессия (Менеджер проектов) ===")
    
    agent = ProfessionValidatorAgent(
        profession_title="Менеджер проектов",
        temperature=0.3,
        max_tokens=2048,
    )
    
    result = await agent.validate_profession()
    print(json.dumps(result, ensure_ascii=False, indent=2))


async def main():
    """Запуск всех тестов"""
    print("🚀 Начинаем тестирование агента валидации профессий\n")
    
    try:
        # Можно запускать по одному или все вместе
        await test_valid_profession()
        await test_invalid_profession()
        # await test_rare_profession()
        # await test_general_profession()
        # await test_popular_profession()
        
        print("\n✅ Тестирование завершено")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")


if __name__ == "__main__":
    asyncio.run(main())

