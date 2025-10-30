# 📸 Руководство по API генерации изображений для фронтенда

## Содержание
- [Введение](#введение)
- [Эндпоинты](#эндпоинты)
- [Генерация изображения](#генерация-изображения)
- [Получение стилей](#получение-стилей)
- [Проверка статуса сервиса](#проверка-статуса-сервиса)
- [Примеры использования](#примеры-использования)
- [Обработка ошибок](#обработка-ошибок)
- [Лучшие практики](#лучшие-практики)

---

## Введение

API генерации изображений использует **Kandinsky** от Fusion Brain для создания изображений на основе текстовых описаний.

### Базовые параметры
- **Base URL**: `http://localhost:8000` (или URL вашего бэкенда)
- **Авторизация**: Bearer токен в заголовке `Authorization`
- **Content-Type**: `application/json`

---

## Эндпоинты

### 1. Генерация изображения
```
POST /images/generate
```

### 2. Получение доступных стилей
```
GET /images/styles
```

### 3. Проверка статуса сервиса
```
GET /images/status
```

---

## Генерация изображения

### Запрос

**Endpoint**: `POST /images/generate`

**Headers**:
```json
{
  "Authorization": "Bearer YOUR_ACCESS_TOKEN",
  "Content-Type": "application/json"
}
```

**Body**:
```json
{
  "prompt": "Пушистый кот в очках на фоне космоса",
  "width": 1024,
  "height": 1024,
  "style": "ANIME",
  "negative_prompt": "яркие цвета, размытость"
}
```

### Параметры запроса

| Параметр | Тип | Обязательный | Описание | Значение по умолчанию |
|----------|-----|--------------|----------|----------------------|
| `prompt` | string | ✅ Да | Текстовое описание изображения (макс 1000 символов) | - |
| `width` | integer | ❌ Нет | Ширина в пикселях (кратно 64, от 64 до 1024) | 1024 |
| `height` | integer | ❌ Нет | Высота в пикселях (кратно 64, от 64 до 1024) | 1024 |
| `style` | string | ❌ Нет | Стиль генерации (см. список стилей) | null |
| `negative_prompt` | string | ❌ Нет | Что НЕ должно быть на изображении (макс 1000 символов) | null |

### ⚠️ Важные ограничения

1. **Размеры должны быть кратны 64**: 64, 128, 192, 256, 320, 384, 448, 512, 576, 640, 704, 768, 832, 896, 960, 1024
2. **Максимальный размер**: 1024x1024 пикселей
3. **Рекомендуемые соотношения сторон**:
   - 1:1 (1024x1024) - квадрат
   - 2:3 (704x1024) - портрет
   - 3:2 (1024x704) - альбом
   - 9:16 (576x1024) - вертикальное видео
   - 16:9 (1024x576) - горизонтальное видео

### Ответ

**Status**: `200 OK`

```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "prompt": "Пушистый кот в очках на фоне космоса",
  "width": 1024,
  "height": 1024,
  "style": "ANIME"
}
```

### Поля ответа

| Поле | Тип | Описание |
|------|-----|----------|
| `image_base64` | string | Изображение в формате Base64 |
| `prompt` | string | Использованный промпт |
| `width` | integer | Ширина изображения |
| `height` | integer | Высота изображения |
| `style` | string/null | Использованный стиль |

### 🖼️ Отображение изображения

Чтобы отобразить Base64 изображение:

```javascript
// В React
<img src={`data:image/png;base64,${imageData.image_base64}`} alt="Generated" />

// В HTML
<img src="data:image/png;base64,iVBORw0KGgo..." alt="Generated">
```

### ⏱️ Время генерации

- **Минимум**: 30-60 секунд
- **Обычно**: 60-120 секунд
- **Максимум**: 5 минут (таймаут)

**Важно**: Настройте таймаут запроса минимум на 6 минут!

---

## Получение стилей

### Запрос

**Endpoint**: `GET /images/styles`

**Headers**:
```json
{
  "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}
```

### Ответ

**Status**: `200 OK`

```json
{
  "styles": [
    {
      "name": "KANDINSKY",
      "title": "Кандинский",
      "titleEn": "Kandinsky",
      "image": "https://cdn.fusionbrain.ai/static/styles/kandinsky.jpg"
    },
    {
      "name": "ANIME",
      "title": "Аниме",
      "titleEn": "Anime",
      "image": "https://cdn.fusionbrain.ai/static/styles/anime.jpg"
    },
    {
      "name": "UHD",
      "title": "Ультра HD",
      "titleEn": "Ultra HD",
      "image": "https://cdn.fusionbrain.ai/static/styles/uhd.jpg"
    }
  ],
  "total": 3
}
```

### Использование

Получите стили при загрузке страницы и покажите пользователю в виде выбора:

```javascript
const styles = await fetchStyles();
// Отобразите в dropdown или в виде карточек с превью
```

---

## Проверка статуса сервиса

### Запрос

**Endpoint**: `GET /images/status`

**Headers**:
```json
{
  "Authorization": "Bearer YOUR_ACCESS_TOKEN"
}
```

### Ответ

**Status**: `200 OK`

**Сервис доступен**:
```json
{
  "available": true,
  "status": "Сервис доступен"
}
```

**Сервис недоступен**:
```json
{
  "available": false,
  "status": "Сервис временно недоступен из-за высокой нагрузки"
}
```

### Использование

Проверяйте статус перед отправкой задачи на генерацию:

```javascript
const status = await checkServiceStatus();
if (!status.available) {
  alert("Сервис генерации временно недоступен. Попробуйте позже.");
  return;
}
```

---

## Примеры использования

### JavaScript (Fetch API)

```javascript
// 1. Проверка статуса
async function checkServiceStatus(token) {
  const response = await fetch('http://localhost:8000/images/status', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Ошибка проверки статуса');
  }
  
  return await response.json();
}

// 2. Получение стилей
async function getStyles(token) {
  const response = await fetch('http://localhost:8000/images/styles', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('Ошибка получения стилей');
  }
  
  return await response.json();
}

// 3. Генерация изображения
async function generateImage(token, prompt, options = {}) {
  const {
    width = 1024,
    height = 1024,
    style = null,
    negativePrompt = null
  } = options;
  
  const response = await fetch('http://localhost:8000/images/generate', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: prompt,
      width: width,
      height: height,
      style: style,
      negative_prompt: negativePrompt
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Ошибка генерации');
  }
  
  return await response.json();
}

// Использование
async function example() {
  const token = localStorage.getItem('access_token');
  
  try {
    // Проверяем статус
    const status = await checkServiceStatus(token);
    if (!status.available) {
      alert(status.status);
      return;
    }
    
    // Получаем стили (опционально)
    const stylesData = await getStyles(token);
    console.log('Доступные стили:', stylesData.styles);
    
    // Генерируем изображение
    const result = await generateImage(
      token,
      'Космический корабль в стиле ретро-футуризма',
      {
        width: 1024,
        height: 704,
        style: 'UHD',
        negativePrompt: 'размытость, низкое качество'
      }
    );
    
    // Отображаем изображение
    const img = document.createElement('img');
    img.src = `data:image/png;base64,${result.image_base64}`;
    document.body.appendChild(img);
    
  } catch (error) {
    console.error('Ошибка:', error.message);
    alert('Произошла ошибка: ' + error.message);
  }
}
```

### React + TypeScript

```typescript
import { useState } from 'react';

interface ImageGenerateRequest {
  prompt: string;
  width?: number;
  height?: number;
  style?: string | null;
  negative_prompt?: string | null;
}

interface ImageGenerateResponse {
  image_base64: string;
  prompt: string;
  width: number;
  height: number;
  style: string | null;
}

function ImageGenerator() {
  const [prompt, setPrompt] = useState('');
  const [image, setImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateImage = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Требуется авторизация');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/images/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          prompt: prompt,
          width: 1024,
          height: 1024
        } as ImageGenerateRequest)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Ошибка генерации');
      }

      const data: ImageGenerateResponse = await response.json();
      setImage(data.image_base64);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Генератор изображений</h2>
      
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Опишите желаемое изображение..."
        rows={4}
        style={{ width: '100%' }}
      />
      
      <button 
        onClick={generateImage} 
        disabled={loading || !prompt}
      >
        {loading ? 'Генерация... (это может занять до 2 минут)' : 'Сгенерировать'}
      </button>
      
      {error && <div style={{ color: 'red' }}>{error}</div>}
      
      {image && (
        <div>
          <h3>Результат:</h3>
          <img 
            src={`data:image/png;base64,${image}`} 
            alt="Generated" 
            style={{ maxWidth: '100%' }}
          />
        </div>
      )}
    </div>
  );
}

export default ImageGenerator;
```

### Axios

```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Создаем экземпляр axios с базовой конфигурацией
const api = axios.create({
  baseURL: API_URL,
  timeout: 360000, // 6 минут для генерации изображений
  headers: {
    'Content-Type': 'application/json'
  }
});

// Добавляем токен к каждому запросу
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Генерация изображения
async function generateImage(prompt, options = {}) {
  try {
    const response = await api.post('/images/generate', {
      prompt,
      width: options.width || 1024,
      height: options.height || 1024,
      style: options.style || null,
      negative_prompt: options.negativePrompt || null
    });
    
    return response.data;
  } catch (error) {
    if (error.response) {
      // Сервер вернул ошибку
      throw new Error(error.response.data.detail || 'Ошибка генерации');
    } else if (error.request) {
      // Запрос был отправлен, но ответ не получен
      throw new Error('Нет ответа от сервера. Проверьте подключение.');
    } else {
      throw new Error('Ошибка при создании запроса');
    }
  }
}

// Использование
generateImage('Закат на Марсе', { style: 'UHD' })
  .then(data => {
    console.log('Изображение сгенерировано:', data);
  })
  .catch(error => {
    console.error('Ошибка:', error.message);
  });
```

---

## Обработка ошибок

### Коды ошибок

| Код | Описание | Действие |
|-----|----------|----------|
| `401` | Невалидный токен | Перелогиниться |
| `400` | Неверные параметры | Проверить размеры (кратность 64), длину промпта |
| `408` | Таймаут генерации | Попробовать снова или уменьшить размер |
| `502` | Ошибка Fusion Brain API | Проверить статус сервиса, повторить позже |
| `500` | Внутренняя ошибка сервера | Обратиться к разработчикам |

### Примеры ошибок

**Неверный размер**:
```json
{
  "detail": "Ширина должна быть кратна 64. Ближайшие значения: 960 или 1024"
}
```

**Модерация контента**:
```json
{
  "detail": "Изображение не прошло модерацию контента"
}
```

**Таймаут**:
```json
{
  "detail": "Превышено время ожидания генерации"
}
```

### Обработка ошибок в коде

```javascript
try {
  const result = await generateImage(token, prompt);
  // Успех
} catch (error) {
  if (error.message.includes('кратна 64')) {
    // Показать пользователю подсказку о правильных размерах
    alert('Размеры должны быть кратны 64. Попробуйте 1024x1024');
  } else if (error.message.includes('модерацию')) {
    // Промпт не прошел модерацию
    alert('Описание содержит запрещенный контент. Измените запрос.');
  } else if (error.message.includes('Превышено время')) {
    // Таймаут
    alert('Генерация заняла слишком много времени. Попробуйте еще раз.');
  } else {
    // Другие ошибки
    alert('Произошла ошибка: ' + error.message);
  }
}
```

---

## Лучшие практики

### 1. 🔐 Безопасность

- **Всегда** передавайте токен в заголовке `Authorization`
- **Никогда** не храните токены в коде
- Используйте `localStorage` или `sessionStorage` для токенов

```javascript
// Правильно
const token = localStorage.getItem('access_token');
headers: { 'Authorization': `Bearer ${token}` }

// Неправильно
const token = 'hardcoded-token-123';
```

### 2. ⏱️ Таймауты

- Устанавливайте таймаут минимум **6 минут** (360000 мс)
- Показывайте индикатор загрузки с примерным временем ожидания

```javascript
// Fetch API
const controller = new AbortController();
const timeoutId = setTimeout(() => controller.abort(), 360000); // 6 минут

fetch(url, { signal: controller.signal })
  .finally(() => clearTimeout(timeoutId));

// Axios
axios.create({ timeout: 360000 });
```

### 3. 🎨 UX рекомендации

**Перед генерацией**:
- ✅ Проверяйте статус сервиса
- ✅ Валидируйте промпт (не пустой, до 1000 символов)
- ✅ Предлагайте популярные размеры (1024x1024, 1024x704, и т.д.)
- ✅ Показывайте превью доступных стилей

**Во время генерации**:
- ✅ Показывайте прогресс-бар или анимацию
- ✅ Указывайте примерное время ожидания (1-2 минуты)
- ✅ Блокируйте повторную отправку
- ✅ Добавьте кнопку отмены

**После генерации**:
- ✅ Показывайте превью изображения
- ✅ Добавьте кнопки "Скачать", "Сгенерировать еще"
- ✅ Храните историю промптов

### 4. 📏 Размеры изображений

**Предустановки для пользователей**:

```javascript
const presets = [
  { name: 'Квадрат', width: 1024, height: 1024, ratio: '1:1' },
  { name: 'Портрет', width: 704, height: 1024, ratio: '2:3' },
  { name: 'Альбом', width: 1024, height: 704, ratio: '3:2' },
  { name: 'Вертикальное видео', width: 576, height: 1024, ratio: '9:16' },
  { name: 'Горизонтальное видео', width: 1024, height: 576, ratio: '16:9' }
];
```

### 5. 💾 Скачивание изображений

```javascript
function downloadImage(base64Image, filename = 'generated-image.png') {
  // Создаем ссылку для скачивания
  const link = document.createElement('a');
  link.href = `data:image/png;base64,${base64Image}`;
  link.download = filename;
  
  // Программно кликаем по ссылке
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
```

### 6. 🔄 Повторные попытки

При ошибках сети или таймауте:

```javascript
async function generateWithRetry(token, prompt, maxRetries = 2) {
  let lastError;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await generateImage(token, prompt);
    } catch (error) {
      lastError = error;
      console.log(`Попытка ${i + 1} не удалась, повторяем...`);
      await new Promise(resolve => setTimeout(resolve, 2000)); // Пауза 2 сек
    }
  }
  
  throw lastError;
}
```

### 7. 📝 Валидация промпта

```javascript
function validatePrompt(prompt) {
  if (!prompt || prompt.trim().length === 0) {
    return { valid: false, error: 'Промпт не может быть пустым' };
  }
  
  if (prompt.length > 1000) {
    return { valid: false, error: 'Промпт не должен превышать 1000 символов' };
  }
  
  return { valid: true };
}

// Использование
const validation = validatePrompt(userInput);
if (!validation.valid) {
  alert(validation.error);
  return;
}
```

### 8. 🎯 Примеры хороших промптов

Подскажите пользователям, как составлять эффективные промпты:

**Хорошие промпты**:
- ✅ "Реалистичный закат над океаном с облаками в золотых тонах"
- ✅ "Футуристический город с небоскребами и летающими машинами, неоновая подсветка"
- ✅ "Милый котенок в стиле аниме с большими глазами, пастельные тона"

**Плохие промпты**:
- ❌ "кот" (слишком общее)
- ❌ "нарисуй красиво" (неконкретно)
- ❌ Очень длинные промпты с излишними деталями

---

## 🎉 Готовые примеры интеграции

### Минимальный пример (HTML + JavaScript)

```html
<!DOCTYPE html>
<html>
<head>
  <title>Генератор изображений</title>
  <style>
    body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
    textarea { width: 100%; padding: 10px; margin: 10px 0; }
    button { padding: 10px 20px; font-size: 16px; cursor: pointer; }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
    #result img { max-width: 100%; margin-top: 20px; }
    .error { color: red; margin: 10px 0; }
    .loading { color: blue; margin: 10px 0; }
  </style>
</head>
<body>
  <h1>🎨 Генератор изображений AI</h1>
  
  <div>
    <label>Опишите изображение:</label>
    <textarea id="prompt" rows="4" placeholder="Например: Космический корабль в стиле ретро-футуризма"></textarea>
  </div>
  
  <button id="generateBtn" onclick="generate()">Сгенерировать изображение</button>
  
  <div id="status"></div>
  <div id="result"></div>

  <script>
    const API_URL = 'http://localhost:8000';
    const TOKEN = localStorage.getItem('access_token'); // Получите токен после логина

    async function generate() {
      const prompt = document.getElementById('prompt').value;
      const statusDiv = document.getElementById('status');
      const resultDiv = document.getElementById('result');
      const btn = document.getElementById('generateBtn');
      
      if (!prompt.trim()) {
        alert('Введите описание изображения');
        return;
      }
      
      btn.disabled = true;
      statusDiv.className = 'loading';
      statusDiv.textContent = 'Генерация изображения... Это может занять 1-2 минуты. Пожалуйста, подождите.';
      resultDiv.innerHTML = '';
      
      try {
        const response = await fetch(`${API_URL}/images/generate`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${TOKEN}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            prompt: prompt,
            width: 1024,
            height: 1024
          })
        });
        
        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.detail || 'Ошибка генерации');
        }
        
        const data = await response.json();
        
        statusDiv.className = '';
        statusDiv.textContent = '✅ Изображение успешно сгенерировано!';
        resultDiv.innerHTML = `<img src="data:image/png;base64,${data.image_base64}" alt="Generated">`;
        
      } catch (error) {
        statusDiv.className = 'error';
        statusDiv.textContent = '❌ Ошибка: ' + error.message;
      } finally {
        btn.disabled = false;
      }
    }
  </script>
</body>
</html>
```

---

## 📞 Поддержка

При возникновении проблем:

1. Проверьте правильность токена авторизации
2. Убедитесь, что API ключи Fusion Brain настроены в `.env`
3. Проверьте статус сервиса через `/images/status`
4. Проверьте параметры запроса (размеры кратны 64)
5. Увеличьте таймаут запроса

---

## 🔗 Полезные ссылки

- [Документация FastAPI](https://fastapi.tiangolo.com/)
- [Fusion Brain официальный сайт](https://fusionbrain.ai/)
- [Kandinsky модели](https://github.com/ai-forever/Kandinsky-2)

---

**Удачной интеграции! 🚀**

