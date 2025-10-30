# ⚙️ Настройка переменных окружения

## Fusion Brain API ключи

Для работы с генерацией изображений необходимо добавить в ваш `.env` файл следующие переменные:

```env
# Fusion Brain API для генерации изображений (Kandinsky)
FUSION_BRAIN_API_KEY=your-fusion-brain-api-key
FUSION_BRAIN_SECRET_KEY=your-fusion-brain-secret-key
FUSION_BRAIN_API_URL=https://api-key.fusionbrain.ai/
```

## Как получить API ключи

1. Зарегистрируйтесь на [https://fusionbrain.ai/](https://fusionbrain.ai/)
2. Перейдите в раздел API
3. Создайте новый API ключ
4. Скопируйте:
   - **API Key** (X-Key)
   - **Secret Key** (X-Secret)

## Пример полного .env файла

```env
# Основные настройки приложения
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# База данных
DATABASE_PATH=data/career_ai.db

# CORS настройки (разделенные запятыми)
ALLOWED_ORIGINS=*

# ElevenLabs API для генерации аудио
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Fusion Brain API для генерации изображений (Kandinsky)
FUSION_BRAIN_API_KEY=ваш-ключ-здесь
FUSION_BRAIN_SECRET_KEY=ваш-секрет-здесь
FUSION_BRAIN_API_URL=https://api-key.fusionbrain.ai/
```

## Проверка настройки

После добавления ключей перезапустите сервер:

```bash
python main.py
```

Проверьте работоспособность:
1. Авторизуйтесь в приложении
2. Откройте документацию API: http://localhost:8000/docs
3. Найдите раздел "Image Generation"
4. Попробуйте эндпоинт `/images/status` - он должен вернуть статус сервиса

