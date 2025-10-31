# 🗺️ Career Roadmap API - Руководство для фронтенда

Полное руководство по интеграции API генерации карьерного roadmap на фронтенде.

## 📋 Содержание

- [Обзор](#обзор)
- [Эндпоинты](#эндпоинты)
- [Структура данных](#структура-данных)
- [Примеры интеграции](#примеры-интеграции)
- [Компоненты для отображения](#компоненты-для-отображения)
- [Обработка ошибок](#обработка-ошибок)
- [Best Practices](#best-practices)

---

## Обзор

Career Roadmap API генерирует подробный карьерный план развития для выбранной профессии. Roadmap включает:

- **5 этапов развития**: от новичка до эксперта
- **Персонализация**: на основе данных личности (MBTI) и астрологии
- **Детальный контент**: навыки, инструменты, проекты, ресурсы для каждого этапа
- **Вехи**: ключевые достижения на карьерном пути
- **Сертификации**: рекомендуемые сертификаты для каждого уровня
- **Карьерные пути**: возможные направления специализации

---

## Эндпоинты

### 1. Генерация Roadmap

**POST** `/roadmap/generate`

Генерирует персонализированный карьерный roadmap для выбранной профессии.

#### Заголовки запроса

```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

#### Тело запроса

```json
{
  "profession_title": "Backend Python разработчик",
  "current_level": "BEGINNER"  // опционально: BEGINNER, JUNIOR, MIDDLE, SENIOR, EXPERT
}
```

#### Ответ (200 OK)

```json
{
  "roadmap": {
    "profession": "Backend Python разработчик",
    "overview": {
      "description": "Описание профессии и карьерного пути",
      "totalDuration": "5-7 лет до уровня эксперта",
      "keySkills": ["Python", "Django/FastAPI", "SQL", "REST API", "Docker"],
      "personalityInsight": "Ваш аналитический склад ума идеально подходит для Backend разработки...",
      "astrologyInsight": "Как Водолей, вы склонны к инновациям и технологиям..."
    },
    "stages": [
      {
        "id": "stage-1",
        "level": "BEGINNER",
        "title": "Основы программирования",
        "duration": "0-6 месяцев",
        "description": "Изучение базовых концепций Python и веб-разработки",
        "goals": [
          "Освоить синтаксис Python",
          "Понять основы HTTP и REST API",
          "Научиться работать с Git"
        ],
        "skills": [
          {
            "name": "Python основы",
            "description": "Синтаксис, структуры данных, ООП",
            "importance": "high"
          }
        ],
        "tools": [
          {
            "name": "Python 3.10+",
            "category": "language",
            "description": "Основной язык программирования"
          },
          {
            "name": "VS Code",
            "category": "software",
            "description": "Редактор кода"
          }
        ],
        "projects": [
          {
            "title": "REST API для ToDo листа",
            "description": "Создать простой API с CRUD операциями",
            "skills": ["Python", "FastAPI", "SQLite"]
          }
        ],
        "resources": [
          {
            "type": "course",
            "title": "Python для начинающих",
            "description": "Базовый курс от основ до веб-разработки",
            "link": "https://example.com/python-course"
          }
        ],
        "tips": [
          "Практикуйтесь ежедневно минимум 2 часа",
          "Используйте свою аналитичность для глубокого понимания концепций"
        ]
      }
      // ... остальные 4 этапа (JUNIOR, MIDDLE, SENIOR, EXPERT)
    ],
    "milestones": [
      {
        "id": "milestone-1",
        "title": "Первый рабочий проект",
        "stage": "BEGINNER",
        "description": "Завершение первого полноценного проекта",
        "criteria": [
          "API с минимум 5 эндпоинтами",
          "Рабочая база данных",
          "Документация API"
        ]
      }
      // ... еще 8-15 вех
    ],
    "certifications": [
      {
        "name": "Python Institute PCEP",
        "provider": "Python Institute",
        "stage": "BEGINNER",
        "description": "Базовая сертификация по Python",
        "optional": false
      }
      // ... еще 3-8 сертификаций
    ],
    "careerPaths": [
      {
        "title": "Microservices Architect",
        "description": "Специализация на микросервисной архитектуре",
        "fromStage": "MIDDLE",
        "skills": ["Kubernetes", "Docker", "gRPC", "Message Queues"]
      }
      // ... еще 3-5 направлений
    ]
  },
  "has_personality_data": true,
  "has_astrology_data": true
}
```

### 2. Health Check

**GET** `/roadmap/health`

Проверка доступности сервиса roadmap.

#### Ответ (200 OK)

```json
{
  "status": "healthy",
  "service": "roadmap",
  "message": "Career Roadmap Generator is operational"
}
```

---

## Структура данных

### RoadmapOverview

Общий обзор карьерного пути.

```typescript
interface RoadmapOverview {
  description: string;           // Описание профессии
  totalDuration: string;          // Общее время до уровня эксперта
  keySkills: string[];            // Ключевые навыки (5-7)
  personalityInsight?: string;    // Инсайт на основе личности
  astrologyInsight?: string;      // Инсайт на основе астрологии
}
```

### RoadmapStage

Один этап карьерного развития.

```typescript
interface RoadmapStage {
  id: string;                     // stage-1, stage-2, etc.
  level: "BEGINNER" | "JUNIOR" | "MIDDLE" | "SENIOR" | "EXPERT";
  title: string;                  // Название этапа
  duration: string;               // Длительность (например, "0-6 месяцев")
  description: string;            // Описание этапа
  goals: string[];                // Цели этапа (3-5)
  skills: RoadmapSkill[];         // Навыки для изучения (3-7)
  tools: RoadmapTool[];           // Инструменты (3-10)
  projects: RoadmapProject[];     // Проекты для практики (2-4)
  resources: RoadmapResource[];   // Ресурсы для обучения (3-6)
  tips: string[];                 // Персонализированные советы (2-4)
}
```

### RoadmapSkill

Навык для изучения.

```typescript
interface RoadmapSkill {
  name: string;                   // Название навыка
  description: string;            // Что включает навык
  importance: "high" | "medium" | "low";
}
```

### RoadmapTool

Инструмент или технология.

```typescript
interface RoadmapTool {
  name: string;                   // Название инструмента
  category: "framework" | "language" | "platform" | "software" | "tool";
  description: string;            // Краткое описание
}
```

### RoadmapProject

Проект для практики.

```typescript
interface RoadmapProject {
  title: string;                  // Название проекта
  description: string;            // Что нужно сделать и зачем
  skills: string[];               // Какие навыки применяются
}
```

### RoadmapResource

Ресурс для обучения.

```typescript
interface RoadmapResource {
  type: "course" | "book" | "video" | "documentation" | "community" | "certification";
  title: string;                  // Название ресурса
  description: string;            // Почему ресурс полезен
  link?: string;                  // URL (может отсутствовать)
}
```

### RoadmapMilestone

Важная веха на карьерном пути.

```typescript
interface RoadmapMilestone {
  id: string;                     // milestone-1, milestone-2, etc.
  title: string;                  // Название вехи
  stage: string;                  // К какому этапу относится
  description: string;            // Что означает достижение
  criteria: string[];             // Критерии успеха
}
```

### RoadmapCertification

Рекомендуемая сертификация.

```typescript
interface RoadmapCertification {
  name: string;                   // Название сертификации
  provider: string;               // Организация
  stage: string;                  // На каком этапе рекомендуется
  description: string;            // Ценность сертификации
  optional: boolean;              // Обязательна или нет
}
```

### RoadmapCareerPath

Направление специализации.

```typescript
interface RoadmapCareerPath {
  title: string;                  // Название направления
  description: string;            // Что включает
  fromStage: string;              // С какого этапа доступно
  skills: string[];               // Необходимые навыки
}
```

---

## Примеры интеграции

### JavaScript (Fetch API)

```javascript
async function generateRoadmap(professionTitle, currentLevel = null) {
  const token = localStorage.getItem('jwt_token');
  
  try {
    const response = await fetch('http://localhost:8000/roadmap/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        profession_title: professionTitle,
        current_level: currentLevel,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Ошибка генерации roadmap');
    }

    const data = await response.json();
    return data.roadmap;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}

// Использование
generateRoadmap('Backend Python разработчик', 'BEGINNER')
  .then(roadmap => {
    console.log('Roadmap сгенерирован:', roadmap);
    displayRoadmap(roadmap);
  })
  .catch(error => {
    console.error('Ошибка:', error.message);
  });
```

### React + TypeScript

```typescript
import React, { useState } from 'react';
import axios from 'axios';

interface RoadmapGenerateRequest {
  profession_title: string;
  current_level?: string;
}

interface RoadmapGenerateResponse {
  roadmap: ProfessionRoadmap;
  has_personality_data: boolean;
  has_astrology_data: boolean;
}

const RoadmapGenerator: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [roadmap, setRoadmap] = useState<ProfessionRoadmap | null>(null);
  const [error, setError] = useState<string>('');

  const generateRoadmap = async (professionTitle: string, currentLevel?: string) => {
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('jwt_token');
      const response = await axios.post<RoadmapGenerateResponse>(
        'http://localhost:8000/roadmap/generate',
        {
          profession_title: professionTitle,
          current_level: currentLevel,
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      setRoadmap(response.data.roadmap);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка генерации roadmap');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <button 
        onClick={() => generateRoadmap('Backend Python разработчик', 'BEGINNER')}
        disabled={loading}
      >
        {loading ? 'Генерация...' : 'Сгенерировать Roadmap'}
      </button>

      {error && <div className="error">{error}</div>}
      
      {roadmap && <RoadmapDisplay roadmap={roadmap} />}
    </div>
  );
};
```

### Vue 3 + TypeScript

```typescript
<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';

const loading = ref(false);
const roadmap = ref<ProfessionRoadmap | null>(null);
const error = ref('');

const generateRoadmap = async (professionTitle: string, currentLevel?: string) => {
  loading.value = true;
  error.value = '';

  try {
    const token = localStorage.getItem('jwt_token');
    const { data } = await axios.post(
      'http://localhost:8000/roadmap/generate',
      {
        profession_title: professionTitle,
        current_level: currentLevel,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    roadmap.value = data.roadmap;
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Ошибка генерации roadmap';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div>
    <button @click="generateRoadmap('Backend Python разработчик', 'BEGINNER')" :disabled="loading">
      {{ loading ? 'Генерация...' : 'Сгенерировать Roadmap' }}
    </button>

    <div v-if="error" class="error">{{ error }}</div>
    
    <RoadmapDisplay v-if="roadmap" :roadmap="roadmap" />
  </div>
</template>
```

---

## Компоненты для отображения

### 1. Обзор Roadmap

```typescript
// RoadmapOverview.tsx
interface Props {
  overview: RoadmapOverview;
  profession: string;
}

const RoadmapOverviewComponent: React.FC<Props> = ({ overview, profession }) => {
  return (
    <div className="roadmap-overview">
      <h1>🗺️ Career Roadmap: {profession}</h1>
      
      <div className="overview-description">
        <p>{overview.description}</p>
        <p><strong>Общая длительность:</strong> {overview.totalDuration}</p>
      </div>

      <div className="key-skills">
        <h3>🔑 Ключевые навыки</h3>
        <div className="skills-tags">
          {overview.keySkills.map((skill, index) => (
            <span key={index} className="skill-tag">{skill}</span>
          ))}
        </div>
      </div>

      {overview.personalityInsight && (
        <div className="insight personality">
          <h4>💡 Личностный инсайт</h4>
          <p>{overview.personalityInsight}</p>
        </div>
      )}

      {overview.astrologyInsight && (
        <div className="insight astrology">
          <h4>⭐ Астрологический инсайт</h4>
          <p>{overview.astrologyInsight}</p>
        </div>
      )}
    </div>
  );
};
```

### 2. Этапы развития (Timeline)

```typescript
// RoadmapTimeline.tsx
interface Props {
  stages: RoadmapStage[];
}

const RoadmapTimeline: React.FC<Props> = ({ stages }) => {
  const [activeStage, setActiveStage] = useState(0);

  const stageColors = {
    BEGINNER: '#4CAF50',
    JUNIOR: '#2196F3',
    MIDDLE: '#FF9800',
    SENIOR: '#9C27B0',
    EXPERT: '#F44336',
  };

  return (
    <div className="roadmap-timeline">
      <div className="timeline-nav">
        {stages.map((stage, index) => (
          <button
            key={stage.id}
            className={`timeline-step ${activeStage === index ? 'active' : ''}`}
            style={{ backgroundColor: stageColors[stage.level] }}
            onClick={() => setActiveStage(index)}
          >
            <div className="step-number">{index + 1}</div>
            <div className="step-label">{stage.level}</div>
            <div className="step-duration">{stage.duration}</div>
          </button>
        ))}
      </div>

      <div className="stage-content">
        <StageDetail stage={stages[activeStage]} />
      </div>
    </div>
  );
};
```

### 3. Детали этапа

```typescript
// StageDetail.tsx
interface Props {
  stage: RoadmapStage;
}

const StageDetail: React.FC<Props> = ({ stage }) => {
  return (
    <div className="stage-detail">
      <div className="stage-header">
        <h2>{stage.title}</h2>
        <p className="stage-description">{stage.description}</p>
      </div>

      {/* Цели */}
      <section className="stage-section">
        <h3>🎯 Цели</h3>
        <ul>
          {stage.goals.map((goal, index) => (
            <li key={index}>{goal}</li>
          ))}
        </ul>
      </section>

      {/* Навыки */}
      <section className="stage-section">
        <h3>🔧 Навыки</h3>
        <div className="skills-grid">
          {stage.skills.map((skill, index) => (
            <div key={index} className={`skill-card importance-${skill.importance}`}>
              <h4>{skill.name}</h4>
              <p>{skill.description}</p>
              <span className="importance-badge">{skill.importance}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Инструменты */}
      <section className="stage-section">
        <h3>🛠️ Инструменты и технологии</h3>
        <div className="tools-list">
          {stage.tools.map((tool, index) => (
            <div key={index} className="tool-item">
              <span className="tool-name">{tool.name}</span>
              <span className="tool-category">{tool.category}</span>
              <p className="tool-description">{tool.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Проекты */}
      <section className="stage-section">
        <h3>💻 Проекты для практики</h3>
        <div className="projects-list">
          {stage.projects.map((project, index) => (
            <div key={index} className="project-card">
              <h4>{project.title}</h4>
              <p>{project.description}</p>
              <div className="project-skills">
                {project.skills.map((skill, i) => (
                  <span key={i} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Ресурсы */}
      <section className="stage-section">
        <h3>📚 Ресурсы для обучения</h3>
        <div className="resources-list">
          {stage.resources.map((resource, index) => (
            <div key={index} className="resource-item">
              <span className="resource-type">{resource.type}</span>
              <h4>{resource.title}</h4>
              <p>{resource.description}</p>
              {resource.link && (
                <a href={resource.link} target="_blank" rel="noopener noreferrer">
                  Перейти →
                </a>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* Советы */}
      <section className="stage-section tips">
        <h3>💡 Персональные советы</h3>
        <ul>
          {stage.tips.map((tip, index) => (
            <li key={index}>{tip}</li>
          ))}
        </ul>
      </section>
    </div>
  );
};
```

### 4. Вехи (Milestones)

```typescript
// MilestonesView.tsx
interface Props {
  milestones: RoadmapMilestone[];
}

const MilestonesView: React.FC<Props> = ({ milestones }) => {
  return (
    <div className="milestones-container">
      <h2>🏆 Ключевые вехи</h2>
      <div className="milestones-list">
        {milestones.map((milestone) => (
          <div key={milestone.id} className="milestone-card">
            <div className="milestone-header">
              <h3>{milestone.title}</h3>
              <span className="milestone-stage">{milestone.stage}</span>
            </div>
            <p className="milestone-description">{milestone.description}</p>
            <div className="milestone-criteria">
              <h4>Критерии успеха:</h4>
              <ul>
                {milestone.criteria.map((criterion, index) => (
                  <li key={index}>{criterion}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 5. Сертификации

```typescript
// CertificationsView.tsx
interface Props {
  certifications: RoadmapCertification[];
}

const CertificationsView: React.FC<Props> = ({ certifications }) => {
  const groupedByStage = certifications.reduce((acc, cert) => {
    if (!acc[cert.stage]) acc[cert.stage] = [];
    acc[cert.stage].push(cert);
    return acc;
  }, {} as Record<string, RoadmapCertification[]>);

  return (
    <div className="certifications-container">
      <h2>📜 Рекомендуемые сертификации</h2>
      {Object.entries(groupedByStage).map(([stage, certs]) => (
        <div key={stage} className="certifications-stage">
          <h3>{stage}</h3>
          <div className="certifications-grid">
            {certs.map((cert, index) => (
              <div key={index} className={`cert-card ${cert.optional ? 'optional' : 'required'}`}>
                <h4>{cert.name}</h4>
                <p className="cert-provider">от {cert.provider}</p>
                <p className="cert-description">{cert.description}</p>
                <span className="cert-badge">
                  {cert.optional ? 'Опционально' : 'Рекомендуется'}
                </span>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};
```

### 6. Карьерные пути

```typescript
// CareerPathsView.tsx
interface Props {
  careerPaths: RoadmapCareerPath[];
}

const CareerPathsView: React.FC<Props> = ({ careerPaths }) => {
  return (
    <div className="career-paths-container">
      <h2>🚀 Направления специализации</h2>
      <div className="paths-grid">
        {careerPaths.map((path, index) => (
          <div key={index} className="path-card">
            <div className="path-header">
              <h3>{path.title}</h3>
              <span className="path-stage">Доступно с: {path.fromStage}</span>
            </div>
            <p className="path-description">{path.description}</p>
            <div className="path-skills">
              <h4>Необходимые навыки:</h4>
              <div className="skills-tags">
                {path.skills.map((skill, i) => (
                  <span key={i} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## Обработка ошибок

### Типичные ошибки и их обработка

#### 1. Ошибка авторизации (401)

```typescript
if (error.response?.status === 401) {
  // Токен недействителен или истек
  localStorage.removeItem('jwt_token');
  redirectToLogin();
}
```

#### 2. Пользователь не найден (404)

```typescript
if (error.response?.status === 404) {
  showError('Пользователь не найден. Пожалуйста, войдите снова.');
}
```

#### 3. Ошибка валидации (400)

```typescript
if (error.response?.status === 400) {
  const message = error.response.data.detail;
  showError(`Ошибка валидации: ${message}`);
}
```

#### 4. Внутренняя ошибка сервера (500)

```typescript
if (error.response?.status === 500) {
  showError('Произошла внутренняя ошибка. Попробуйте позже.');
  // Опционально: отправить отчет об ошибке
  sendErrorReport(error);
}
```

### Полный пример обработки ошибок

```typescript
async function handleRoadmapGeneration(professionTitle: string) {
  try {
    setLoading(true);
    const roadmap = await generateRoadmap(professionTitle);
    setRoadmap(roadmap);
    showSuccess('Roadmap успешно сгенерирован!');
  } catch (error: any) {
    // Обработка по типу ошибки
    if (error.response) {
      switch (error.response.status) {
        case 401:
          showError('Необходима авторизация');
          redirectToLogin();
          break;
        case 404:
          showError('Пользователь не найден');
          break;
        case 400:
          showError(error.response.data.detail);
          break;
        case 500:
          showError('Внутренняя ошибка сервера. Попробуйте позже.');
          break;
        default:
          showError('Произошла неизвестная ошибка');
      }
    } else if (error.request) {
      // Запрос был отправлен, но ответ не получен
      showError('Не удалось соединиться с сервером');
    } else {
      // Ошибка при настройке запроса
      showError('Ошибка при формировании запроса');
    }
  } finally {
    setLoading(false);
  }
}
```

---

## Best Practices

### 1. Кэширование roadmap

Roadmap генерируется достаточно долго (10-30 секунд), поэтому рекомендуется кэшировать результаты:

```typescript
const CACHE_KEY = 'roadmap_cache';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 часа

function saveRoadmapToCache(professionTitle: string, roadmap: ProfessionRoadmap) {
  const cacheData = {
    roadmap,
    timestamp: Date.now(),
    profession: professionTitle,
  };
  localStorage.setItem(`${CACHE_KEY}_${professionTitle}`, JSON.stringify(cacheData));
}

function getRoadmapFromCache(professionTitle: string): ProfessionRoadmap | null {
  const cached = localStorage.getItem(`${CACHE_KEY}_${professionTitle}`);
  if (!cached) return null;

  const cacheData = JSON.parse(cached);
  const isExpired = Date.now() - cacheData.timestamp > CACHE_DURATION;

  if (isExpired) {
    localStorage.removeItem(`${CACHE_KEY}_${professionTitle}`);
    return null;
  }

  return cacheData.roadmap;
}
```

### 2. Индикатор прогресса

```typescript
const [progress, setProgress] = useState(0);

async function generateRoadmapWithProgress(professionTitle: string) {
  setProgress(10); // Начало запроса
  
  const interval = setInterval(() => {
    setProgress(prev => Math.min(prev + 10, 90));
  }, 2000);

  try {
    const roadmap = await generateRoadmap(professionTitle);
    setProgress(100);
    return roadmap;
  } finally {
    clearInterval(interval);
  }
}
```

### 3. Постепенная загрузка контента

```typescript
// Сначала показываем overview и структуру
function showRoadmapSkeleton(roadmap: ProfessionRoadmap) {
  // Показать обзор сразу
  displayOverview(roadmap.overview);
  
  // Показать названия этапов
  displayStagesStructure(roadmap.stages);
  
  // Постепенно загружать детали каждого этапа
  roadmap.stages.forEach((stage, index) => {
    setTimeout(() => {
      displayStageDetails(stage);
    }, index * 500);
  });
}
```

### 4. Адаптивный дизайн

```css
/* Мобильная версия */
@media (max-width: 768px) {
  .roadmap-timeline {
    flex-direction: column;
  }
  
  .stage-content {
    padding: 1rem;
  }
  
  .skills-grid {
    grid-template-columns: 1fr;
  }
}

/* Десктоп версия */
@media (min-width: 769px) {
  .skills-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}
```

### 5. Экспорт в PDF

```typescript
import jsPDF from 'jspdf';

function exportRoadmapToPDF(roadmap: ProfessionRoadmap) {
  const doc = new jsPDF();
  let yPos = 20;

  // Заголовок
  doc.setFontSize(20);
  doc.text(`Career Roadmap: ${roadmap.profession}`, 20, yPos);
  yPos += 15;

  // Обзор
  doc.setFontSize(12);
  doc.text(roadmap.overview.description, 20, yPos, { maxWidth: 170 });
  yPos += 20;

  // Этапы
  roadmap.stages.forEach((stage, index) => {
    doc.setFontSize(16);
    doc.text(`${index + 1}. ${stage.title}`, 20, yPos);
    yPos += 10;

    doc.setFontSize(10);
    doc.text(`Duration: ${stage.duration}`, 25, yPos);
    yPos += 7;
    
    // Добавить новую страницу при необходимости
    if (yPos > 270) {
      doc.addPage();
      yPos = 20;
    }
  });

  doc.save(`roadmap-${roadmap.profession}.pdf`);
}
```

### 6. Шаринг roadmap

```typescript
async function shareRoadmap(roadmap: ProfessionRoadmap) {
  const shareData = {
    title: `Career Roadmap: ${roadmap.profession}`,
    text: roadmap.overview.description,
    url: window.location.href,
  };

  if (navigator.share) {
    try {
      await navigator.share(shareData);
    } catch (err) {
      console.log('Share failed:', err);
    }
  } else {
    // Fallback: копировать в буфер обмена
    copyToClipboard(window.location.href);
    showToast('Ссылка скопирована в буфер обмена');
  }
}
```

### 7. Отслеживание прогресса пользователя

```typescript
interface UserProgress {
  professionTitle: string;
  currentStage: string;
  completedMilestones: string[];
  completedProjects: string[];
}

function saveUserProgress(progress: UserProgress) {
  localStorage.setItem('user_roadmap_progress', JSON.stringify(progress));
}

function markMilestoneComplete(milestoneId: string) {
  const progress = getUserProgress();
  if (!progress.completedMilestones.includes(milestoneId)) {
    progress.completedMilestones.push(milestoneId);
    saveUserProgress(progress);
    showCelebration('Веха достигнута! 🎉');
  }
}
```

---

## Пример полного компонента

```typescript
// CompleteRoadmapView.tsx
import React, { useState, useEffect } from 'react';
import { generateRoadmap, getRoadmapFromCache, saveRoadmapToCache } from './api';

interface Props {
  professionTitle: string;
  currentLevel?: string;
}

const CompleteRoadmapView: React.FC<Props> = ({ professionTitle, currentLevel }) => {
  const [roadmap, setRoadmap] = useState<ProfessionRoadmap | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeView, setActiveView] = useState<'timeline' | 'milestones' | 'certifications' | 'paths'>('timeline');

  useEffect(() => {
    loadRoadmap();
  }, [professionTitle]);

  const loadRoadmap = async () => {
    // Проверяем кэш
    const cached = getRoadmapFromCache(professionTitle);
    if (cached) {
      setRoadmap(cached);
      return;
    }

    // Генерируем новый
    setLoading(true);
    setError('');

    try {
      const newRoadmap = await generateRoadmap(professionTitle, currentLevel);
      setRoadmap(newRoadmap);
      saveRoadmapToCache(professionTitle, newRoadmap);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="roadmap-loading">
        <div className="spinner" />
        <p>Генерируем ваш персональный roadmap...</p>
        <p className="loading-hint">Это может занять до 30 секунд</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="roadmap-error">
        <h2>Ошибка генерации roadmap</h2>
        <p>{error}</p>
        <button onClick={loadRoadmap}>Попробовать снова</button>
      </div>
    );
  }

  if (!roadmap) return null;

  return (
    <div className="complete-roadmap-view">
      {/* Обзор */}
      <RoadmapOverviewComponent 
        overview={roadmap.overview} 
        profession={roadmap.profession} 
      />

      {/* Навигация */}
      <div className="roadmap-navigation">
        <button 
          className={activeView === 'timeline' ? 'active' : ''}
          onClick={() => setActiveView('timeline')}
        >
          📅 Timeline
        </button>
        <button 
          className={activeView === 'milestones' ? 'active' : ''}
          onClick={() => setActiveView('milestones')}
        >
          🏆 Вехи
        </button>
        <button 
          className={activeView === 'certifications' ? 'active' : ''}
          onClick={() => setActiveView('certifications')}
        >
          📜 Сертификации
        </button>
        <button 
          className={activeView === 'paths' ? 'active' : ''}
          onClick={() => setActiveView('paths')}
        >
          🚀 Карьерные пути
        </button>
      </div>

      {/* Контент */}
      <div className="roadmap-content">
        {activeView === 'timeline' && <RoadmapTimeline stages={roadmap.stages} />}
        {activeView === 'milestones' && <MilestonesView milestones={roadmap.milestones} />}
        {activeView === 'certifications' && <CertificationsView certifications={roadmap.certifications} />}
        {activeView === 'paths' && <CareerPathsView careerPaths={roadmap.careerPaths} />}
      </div>

      {/* Действия */}
      <div className="roadmap-actions">
        <button onClick={() => exportRoadmapToPDF(roadmap)}>
          📄 Экспорт в PDF
        </button>
        <button onClick={() => shareRoadmap(roadmap)}>
          🔗 Поделиться
        </button>
        <button onClick={() => printRoadmap(roadmap)}>
          🖨️ Печать
        </button>
      </div>
    </div>
  );
};

export default CompleteRoadmapView;
```

---

## Заключение

Career Roadmap API предоставляет мощный инструмент для создания персонализированных карьерных планов. Следуйте этому руководству для успешной интеграции на фронтенде.

### Ключевые моменты:

✅ **Персонализация** - roadmap учитывает личность и астрологию пользователя  
✅ **Детальность** - 5 этапов с навыками, инструментами, проектами и ресурсами  
✅ **Практичность** - конкретные советы и критерии успеха  
✅ **Гибкость** - можно начать с любого уровня  
✅ **Визуализация** - timeline, карточки, графики прогресса  

### Дополнительные возможности:

- 🎯 Трекинг прогресса пользователя
- 📊 Визуализация достижений
- 🏆 Геймификация с наградами
- 📱 Мобильная оптимизация
- 💾 Экспорт и шаринг
- 🔔 Напоминания о целях

---

**Документация обновлена:** 30.10.2025  
**Версия API:** 1.0.0  
**Backend:** FastAPI + Python 3.10+

