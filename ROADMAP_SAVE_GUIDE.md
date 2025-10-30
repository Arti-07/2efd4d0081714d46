# 💾 Сохранение Roadmap - Руководство для фронтенда

## ✅ Что реализовано на бэкенде

Roadmap теперь **автоматически сохраняются** в БД при генерации! 

Каждый пользователь может:
- ✅ Сохранять несколько roadmaps для разных профессий
- ✅ Получать сохраненный roadmap по профессии
- ✅ Получать список всех своих roadmaps
- ✅ Удалять roadmaps

---

## 📊 API Endpoints

### 1. POST `/roadmap/generate` - Генерация + Сохранение

**Изменение:** Теперь **автоматически сохраняет** roadmap в БД после генерации!

```typescript
// Ничего не меняется на фронте!
const response = await axios.post(
  'http://localhost:8000/roadmap/generate',
  { profession_title: "Backend Python разработчик" },
  { headers: { Authorization: `Bearer ${token}` } }
);

// Roadmap уже сохранен в БД! ✅
const roadmap = response.data.roadmap;
```

**Логика:**
- Если roadmap для этой профессии уже существует → обновляет его
- Если новая профессия → создает новый roadmap
- Каждый пользователь может иметь roadmap для каждой профессии

---

### 2. GET `/roadmap/saved/{profession_title}` - Получить сохраненный roadmap

Получить roadmap для конкретной профессии без повторной генерации.

**Запрос:**
```typescript
const professionTitle = "Backend Python разработчик";
const response = await axios.get(
  `http://localhost:8000/roadmap/saved/${encodeURIComponent(professionTitle)}`,
  { headers: { Authorization: `Bearer ${token}` } }
);
```

**Ответ (200 OK):**
```json
{
  "id": "uuid-roadmap",
  "profession_title": "Backend Python разработчик",
  "roadmap": {
    "profession": "Backend Python разработчик",
    "overview": { ... },
    "stages": [ ... ]
  },
  "created_at": "2025-10-30T12:00:00",
  "updated_at": "2025-10-30T15:30:00"
}
```

**Ошибки:**
- `404` - Roadmap для этой профессии не найден
- `401` - Невалидный токен

---

### 3. GET `/roadmap/saved` - Получить все roadmaps пользователя

Список всех сохраненных roadmaps.

**Запрос:**
```typescript
const response = await axios.get(
  'http://localhost:8000/roadmap/saved',
  { headers: { Authorization: `Bearer ${token}` } }
);
```

**Ответ (200 OK):**
```json
{
  "roadmaps": [
    {
      "id": "uuid-1",
      "profession_title": "Backend Python разработчик",
      "roadmap": { ... },
      "created_at": "2025-10-30T12:00:00",
      "updated_at": "2025-10-30T15:30:00"
    },
    {
      "id": "uuid-2",
      "profession_title": "Frontend React разработчик",
      "roadmap": { ... },
      "created_at": "2025-10-29T10:00:00",
      "updated_at": "2025-10-29T10:00:00"
    }
  ],
  "total_count": 2
}
```

---

### 4. DELETE `/roadmap/saved/{roadmap_id}` - Удалить roadmap

**Запрос:**
```typescript
const roadmapId = "uuid-roadmap";
const response = await axios.delete(
  `http://localhost:8000/roadmap/saved/${roadmapId}`,
  { headers: { Authorization: `Bearer ${token}` } }
);
```

**Ответ (200 OK):**
```json
{
  "message": "Roadmap успешно удален",
  "roadmap_id": "uuid-roadmap"
}
```

**Ошибки:**
- `404` - Roadmap не найден или не принадлежит пользователю

---

## 🎨 Примеры интеграции

### React: Компонент со списком сохраненных roadmaps

```typescript
import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface SavedRoadmap {
  id: string;
  profession_title: string;
  roadmap: any;
  created_at: string;
  updated_at: string;
}

const SavedRoadmapsList: React.FC = () => {
  const [roadmaps, setRoadmaps] = useState<SavedRoadmap[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSavedRoadmaps();
  }, []);

  const loadSavedRoadmaps = async () => {
    try {
      const token = localStorage.getItem('jwt_token');
      const { data } = await axios.get(
        'http://localhost:8000/roadmap/saved',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setRoadmaps(data.roadmaps);
    } catch (error) {
      console.error('Error loading roadmaps:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteRoadmap = async (roadmapId: string) => {
    if (!confirm('Удалить этот roadmap?')) return;

    try {
      const token = localStorage.getItem('jwt_token');
      await axios.delete(
        `http://localhost:8000/roadmap/saved/${roadmapId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Обновляем список
      setRoadmaps(roadmaps.filter(r => r.id !== roadmapId));
      alert('✅ Roadmap удален');
    } catch (error) {
      alert('❌ Ошибка при удалении');
    }
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="saved-roadmaps-list">
      <h2>Мои Roadmaps ({roadmaps.length})</h2>
      
      {roadmaps.length === 0 ? (
        <p>У вас пока нет сохраненных roadmaps</p>
      ) : (
        <div className="roadmaps-grid">
          {roadmaps.map(item => (
            <div key={item.id} className="roadmap-card">
              <h3>{item.profession_title}</h3>
              <p className="date">
                Обновлен: {new Date(item.updated_at).toLocaleDateString('ru')}
              </p>
              <div className="actions">
                <button onClick={() => viewRoadmap(item)}>
                  👁️ Открыть
                </button>
                <button onClick={() => deleteRoadmap(item.id)}>
                  🗑️ Удалить
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

---

### React: Генерация с проверкой существующего

```typescript
const RoadmapGenerator: React.FC = () => {
  const [professionTitle, setProfessionTitle] = useState('');

  const handleGenerate = async () => {
    try {
      const token = localStorage.getItem('jwt_token');
      
      // 1. Проверяем, есть ли уже сохраненный roadmap
      try {
        const saved = await axios.get(
          `http://localhost:8000/roadmap/saved/${encodeURIComponent(professionTitle)}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        
        // Roadmap уже существует - показываем его
        const useExisting = confirm(
          'У вас уже есть roadmap для этой профессии. Использовать существующий или сгенерировать новый?'
        );
        
        if (useExisting) {
          showRoadmap(saved.data.roadmap);
          return;
        }
      } catch (error: any) {
        // 404 - roadmap не найден, продолжаем генерацию
        if (error.response?.status !== 404) {
          throw error;
        }
      }
      
      // 2. Генерируем новый roadmap (автоматически сохраняется)
      const { data } = await axios.post(
        'http://localhost:8000/roadmap/generate',
        { profession_title: professionTitle },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      showRoadmap(data.roadmap);
      alert('✅ Roadmap сгенерирован и сохранен!');
      
    } catch (error) {
      console.error('Error:', error);
      alert('❌ Ошибка при генерации');
    }
  };

  return (
    <div>
      <input 
        value={professionTitle}
        onChange={(e) => setProfessionTitle(e.target.value)}
        placeholder="Введите профессию"
      />
      <button onClick={handleGenerate}>
        Сгенерировать Roadmap
      </button>
    </div>
  );
};
```

---

### Vue 3: Композабл для работы с roadmaps

```typescript
// useRoadmaps.ts
import { ref } from 'vue';
import axios from 'axios';

export function useRoadmaps() {
  const roadmaps = ref<any[]>([]);
  const loading = ref(false);
  const error = ref('');

  const loadRoadmaps = async () => {
    loading.value = true;
    try {
      const token = localStorage.getItem('jwt_token');
      const { data } = await axios.get(
        'http://localhost:8000/roadmap/saved',
        { headers: { Authorization: `Bearer ${token}` } }
      );
      roadmaps.value = data.roadmaps;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка загрузки';
    } finally {
      loading.value = false;
    }
  };

  const getSavedRoadmap = async (professionTitle: string) => {
    try {
      const token = localStorage.getItem('jwt_token');
      const { data } = await axios.get(
        `http://localhost:8000/roadmap/saved/${encodeURIComponent(professionTitle)}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      return data.roadmap;
    } catch (err: any) {
      if (err.response?.status === 404) {
        return null; // Roadmap не найден
      }
      throw err;
    }
  };

  const generateRoadmap = async (professionTitle: string) => {
    loading.value = true;
    try {
      const token = localStorage.getItem('jwt_token');
      const { data } = await axios.post(
        'http://localhost:8000/roadmap/generate',
        { profession_title: professionTitle },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Roadmap автоматически сохранен!
      return data.roadmap;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка генерации';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const deleteRoadmap = async (roadmapId: string) => {
    try {
      const token = localStorage.getItem('jwt_token');
      await axios.delete(
        `http://localhost:8000/roadmap/saved/${roadmapId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Обновляем локальный список
      roadmaps.value = roadmaps.value.filter(r => r.id !== roadmapId);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Ошибка удаления';
      throw err;
    }
  };

  return {
    roadmaps,
    loading,
    error,
    loadRoadmaps,
    getSavedRoadmap,
    generateRoadmap,
    deleteRoadmap
  };
}
```

**Использование:**
```vue
<script setup lang="ts">
import { onMounted } from 'vue';
import { useRoadmaps } from './useRoadmaps';

const { roadmaps, loading, loadRoadmaps, deleteRoadmap } = useRoadmaps();

onMounted(() => {
  loadRoadmaps();
});
</script>

<template>
  <div class="saved-roadmaps">
    <h2>Мои Roadmaps</h2>
    
    <div v-if="loading">Загрузка...</div>
    
    <div v-else class="roadmaps-grid">
      <div v-for="item in roadmaps" :key="item.id" class="roadmap-card">
        <h3>{{ item.profession_title }}</h3>
        <button @click="deleteRoadmap(item.id)">Удалить</button>
      </div>
    </div>
  </div>
</template>
```

---

## 📱 UI/UX Рекомендации

### 1. Индикатор сохранения

```typescript
// После генерации показываем уведомление
toast.success('✅ Roadmap сохранен в вашем профиле');

// Или добавляем badge
<div className="roadmap-header">
  <h1>{roadmap.profession}</h1>
  <span className="saved-badge">💾 Сохранено</span>
</div>
```

### 2. Список сохраненных roadmaps

```typescript
// В сайдбаре или отдельной странице
<aside className="sidebar">
  <h3>Мои Roadmaps</h3>
  <ul>
    {roadmaps.map(item => (
      <li key={item.id}>
        <a href={`/roadmap/${item.profession_title}`}>
          {item.profession_title}
        </a>
      </li>
    ))}
  </ul>
</aside>
```

### 3. Быстрый доступ к сохраненным

```typescript
// В профиле пользователя
<div className="user-profile">
  <h2>Мои Roadmaps</h2>
  <div className="quick-access">
    {roadmaps.slice(0, 3).map(item => (
      <button 
        key={item.id}
        onClick={() => navigate(`/roadmap/${item.profession_title}`)}
      >
        {item.profession_title}
      </button>
    ))}
  </div>
</div>
```

---

## ✅ Что делать на фронтенде

### Обязательно:

1. ✅ **Ничего не менять** в существующей генерации - roadmap сохраняется автоматически
2. ✅ **Добавить страницу** "Мои Roadmaps" со списком сохраненных
3. ✅ **Добавить кнопку** "Удалить" для каждого roadmap

### Опционально (для лучшего UX):

1. ⭐ Проверять перед генерацией, есть ли уже roadmap
2. ⭐ Показывать уведомление "Roadmap сохранен"
3. ⭐ Добавить быстрый доступ к сохраненным в сайдбар
4. ⭐ Показывать дату последнего обновления
5. ⭐ Добавить поиск по сохраненным roadmaps

---

## 🔄 Flow пользователя

```
1. Пользователь вводит профессию
   ↓
2. Нажимает "Сгенерировать"
   ↓
3. Бэкенд генерирует roadmap
   ↓
4. 💾 Бэкенд АВТОМАТИЧЕСКИ сохраняет в БД
   ↓
5. Фронт получает и показывает roadmap
   ↓
6. Пользователь может:
   - Посмотреть roadmap
   - Скачать PDF
   - Зайти позже в "Мои Roadmaps" и увидеть его там ✅
```

---

## 🎯 Итого

**На бэкенде:**
- ✅ Создана таблица `roadmaps` в БД
- ✅ Roadmap автоматически сохраняется при генерации
- ✅ API для получения/удаления roadmaps готово

**На фронтенде нужно:**
1. Добавить страницу/компонент "Мои Roadmaps"
2. Показывать список с кнопками "Открыть"/"Удалить"
3. Опционально: проверка перед повторной генерацией

**Ничего не ломается!** Все существующие вызовы `/roadmap/generate` работают как раньше, просто теперь roadmap еще и сохраняется! 🚀

