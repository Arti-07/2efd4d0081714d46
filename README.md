<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

# 🚀 Career AI Backend

Backend API для AI-сервиса по выбору карьеры с интеграцией тестов личности, астрологии, генерации аудио и изображений.

</div>

## 📋 Возможности

- ✅ **Аутентификация**: JWT-токены, регистрация и авторизация пользователей
- ✅ **Тесты личности**: Определение типа личности и карьерных рекомендаций
- ✅ **Астрология**: Создание астрологического профиля для карьерных советов
- ✅ **AI Агенты**: Генерация персонализированных карточек профессий
- ✅ **Генерация аудио**: Озвучка текста через ElevenLabs API
- ✅ **Генерация изображений**: Создание изображений через Kandinsky (Fusion Brain API)

## 🆕 Новое: Генерация изображений

Добавлена полная интеграция с **Fusion Brain API (Kandinsky)** для генерации изображений на основе текстовых описаний.

### Эндпоинты:
- `POST /images/generate` - генерация изображения по промпту
- `GET /images/styles` - получение списка доступных стилей
- `GET /images/status` - проверка доступности сервиса

📖 **Подробная документация для фронтенда**: [FRONTEND_IMAGE_API_GUIDE.md](FRONTEND_IMAGE_API_GUIDE.md)

## 🛠️ Установка и запуск

### 1. Клонируйте репозиторий
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Установите зависимости
```bash
pip install -r requirements.txt
```

### 3. Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```env
# Основные настройки
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# База данных
DATABASE_PATH=data/career_ai.db

# CORS
ALLOWED_ORIGINS=*

# ElevenLabs API
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Fusion Brain API (для генерации изображений)
FUSION_BRAIN_API_KEY=your-fusion-brain-api-key
FUSION_BRAIN_SECRET_KEY=your-fusion-brain-secret-key
FUSION_BRAIN_API_URL=https://api-key.fusionbrain.ai/
```

📖 **Подробная инструкция**: [ENV_SETUP.md](ENV_SETUP.md)

### 4. Запустите сервер
```bash
python main.py
```

Сервер будет доступен по адресу: `http://localhost:8000`

## 📚 Документация API

После запуска сервера откройте:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎨 Использование API генерации изображений

### Пример запроса (cURL):
```bash
curl -X POST "http://localhost:8000/images/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Пушистый кот в очках на фоне космоса",
    "width": 1024,
    "height": 1024,
    "style": "ANIME"
  }'
```

### Пример ответа:
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "prompt": "Пушистый кот в очках на фоне космоса",
  "width": 1024,
  "height": 1024,
  "style": "ANIME"
}
```

Полные примеры на JavaScript, React, TypeScript и Axios - в [FRONTEND_IMAGE_API_GUIDE.md](FRONTEND_IMAGE_API_GUIDE.md)

## 📁 Структура проекта

```
.
├── main.py                          # Точка входа FastAPI приложения
├── requirements.txt                 # Python зависимости
├── FRONTEND_IMAGE_API_GUIDE.md      # Документация для фронтенда
├── ENV_SETUP.md                     # Настройка переменных окружения
├── data/
│   └── career_ai.db                 # SQLite база данных
├── src/
│   ├── config.py                    # Конфигурация приложения
│   ├── agent/                       # AI агенты
│   │   ├── core/
│   │   │   ├── career_navigator_agent.py
│   │   │   └── profession_cards_agent.py
│   │   └── prompts/
│   ├── database/                    # Работа с базой данных
│   │   ├── db.py
│   │   ├── personality_db.py
│   │   └── astro_db.py
│   ├── models/                      # Pydantic модели
│   │   ├── auth_model.py
│   │   ├── personality_model.py
│   │   ├── astro_model.py
│   │   ├── vibe_model.py
│   │   ├── audio_model.py
│   │   └── image_model.py           # ← Новое
│   ├── routes/                      # API эндпоинты
│   │   ├── auth_routes.py
│   │   ├── personality_routes.py
│   │   ├── astro_routes.py
│   │   ├── vibe_routes.py
│   │   ├── audio_routes.py
│   │   └── image_routes.py          # ← Новое
│   └── utils/                       # Утилиты
│       ├── auth.py
│       ├── personality_test.py
│       ├── astrology.py
│       └── fusion_brain.py          # ← Новое
```

## 🔑 Основные API эндпоинты

### Аутентификация
- `POST /auth/register` - Регистрация
- `POST /auth/login` - Авторизация

### Личность
- `POST /personality/test/submit` - Отправка теста личности
- `GET /personality/results` - Получение результатов

### Астрология
- `POST /astrology/profile` - Создание астропрофиля
- `GET /astrology/profile` - Получение астропрофиля

### Генерация карточек профессий
- `POST /vibe/generate` - Генерация карточек

### Аудио
- `POST /audio/generate` - Генерация аудио

### **Изображения** 🆕
- `POST /images/generate` - Генерация изображения
- `GET /images/styles` - Список стилей
- `GET /images/status` - Статус сервиса

## 🤝 Интеграция с фронтендом

Для интеграции генерации изображений на фронтенде используйте подробное руководство:

📖 [FRONTEND_IMAGE_API_GUIDE.md](FRONTEND_IMAGE_API_GUIDE.md)

В нем вы найдете:
- ✅ Подробное описание всех эндпоинтов
- ✅ Примеры на JavaScript, React, TypeScript, Axios
- ✅ Готовые HTML примеры
- ✅ Обработка ошибок
- ✅ Лучшие практики UX
- ✅ Валидация и таймауты

## 📞 Поддержка

При возникновении проблем:
1. Проверьте настройку `.env` файла
2. Убедитесь, что API ключи корректны
3. Проверьте логи сервера
4. Изучите документацию в `/docs`

## 📄 Лицензия

MIT