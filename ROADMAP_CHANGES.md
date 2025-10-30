# 🔄 Изменения в Career Roadmap API

Документ описывает изменения, внесенные в Career Roadmap API, и как адаптировать фронтенд под новую структуру.

---

## ⚠️ ВАЖНО: Гарантированные поля

Все поля в roadmap теперь **гарантированно приходят** с бэкенда:
- `interviewQuestions` всегда будет массивом (минимум пустой `[]`, но обычно 5-10 вопросов)
- Никакие поля не будут `undefined`
- Если AI не сгенерирует какое-то поле, оно вернется как пустой массив/строка

---

## 📝 Что изменилось

### ✅ Добавлено

1. **Вопросы на собеседование** (`interviewQuestions`)
   - Каждый этап теперь содержит 5-10 вопросов с ответами
   - Вопросы соответствуют уровню этапа (BEGINNER, JUNIOR, MIDDLE, SENIOR, EXPERT)
   - Формат: `{ question: string, answer: string }`

### ❌ Убрано

1. **Сертификации** (`certifications`) - массив убран из структуры
2. **Вехи** (`milestones`) - массив убран из структуры  
3. **Карьерные пути** (`careerPaths`) - массив убран из структуры
4. **Персональные советы** (`tips`) - убраны из каждого этапа

### 🔧 Улучшено

1. **Экранирование текста**
   - Улучшена обработка специальных символов
   - Исправлены проблемы с символами типа `r/dotnet` → теперь выводится читаемый текст
   - Улучшена обработка слешей и обратных слешей

---

## 📊 Новая структура данных

### ProfessionRoadmap (основной объект)

```typescript
interface ProfessionRoadmap {
  profession: string;
  overview: RoadmapOverview;
  stages: RoadmapStage[];  // 5 этапов
  // УДАЛЕНО: milestones, certifications, careerPaths
}
```

### RoadmapStage (этап развития)

```typescript
interface RoadmapStage {
  id: string;
  level: "BEGINNER" | "JUNIOR" | "MIDDLE" | "SENIOR" | "EXPERT";
  title: string;
  duration: string;
  description: string;
  goals: string[];
  skills: RoadmapSkill[];
  tools: RoadmapTool[];
  projects: RoadmapProject[];
  resources: RoadmapResource[];
  interviewQuestions: InterviewQuestion[];  // ✅ НОВОЕ
  // УДАЛЕНО: tips
}
```

### InterviewQuestion (новый тип)

```typescript
interface InterviewQuestion {
  question: string;  // Вопрос на собеседовании
  answer: string;    // Ответ на вопрос
}
```

---

## 🔄 Что нужно изменить на фронтенде

### 1. Обновить TypeScript интерфейсы

**Удалить:**

```typescript
// ❌ Эти интерфейсы больше не нужны
interface RoadmapMilestone { ... }
interface RoadmapCertification { ... }
interface RoadmapCareerPath { ... }
```

**Добавить:**

```typescript
// ✅ Новый интерфейс
interface InterviewQuestion {
  question: string;
  answer: string;
}
```

**Обновить RoadmapStage:**

```typescript
interface RoadmapStage {
  // ... остальные поля
  interviewQuestions: InterviewQuestion[];  // ✅ Добавить
  // tips: string[];  // ❌ Удалить
}
```

**Обновить ProfessionRoadmap:**

```typescript
interface ProfessionRoadmap {
  profession: string;
  overview: RoadmapOverview;
  stages: RoadmapStage[];
  // milestones: RoadmapMilestone[];      // ❌ Удалить
  // certifications: RoadmapCertification[];  // ❌ Удалить
  // careerPaths: RoadmapCareerPath[];    // ❌ Удалить
}
```

---

### 2. Удалить компоненты для вех, сертификаций, карьерных путей

**Удалить файлы/компоненты:**

- `MilestonesView.tsx` / `MilestonesView.vue`
- `CertificationsView.tsx` / `CertificationsView.vue`
- `CareerPathsView.tsx` / `CareerPathsView.vue`

**Удалить из навигации:**

```typescript
// ❌ Удалить эти кнопки
<button onClick={() => setActiveView('milestones')}>
  🏆 Вехи
</button>
<button onClick={() => setActiveView('certifications')}>
  📜 Сертификации
</button>
<button onClick={() => setActiveView('paths')}>
  🚀 Карьерные пути
</button>
```

---

### 3. Добавить компонент для вопросов на собеседование

**Создать новый компонент `InterviewQuestionsSection.tsx`:**

```typescript
interface Props {
  questions: InterviewQuestion[];
}

const InterviewQuestionsSection: React.FC<Props> = ({ questions }) => {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  // Защита от пустого массива
  if (!questions || questions.length === 0) {
    return null; // Или показать заглушку
  }

  return (
    <section className="stage-section interview-questions">
      <h3>💬 Вопросы на собеседовании</h3>
      <div className="questions-list">
        {questions.map((qa, index) => (
          <div key={index} className="question-card">
            <div 
              className="question-header"
              onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
            >
              <span className="question-number">Q{index + 1}</span>
              <h4 className="question-text">{qa.question}</h4>
              <span className="expand-icon">
                {expandedIndex === index ? '▼' : '▶'}
              </span>
            </div>
            {expandedIndex === index && (
              <div className="answer-content">
                <p>{qa.answer}</p>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};
```

**Стили для компонента:**

```css
.interview-questions {
  margin-top: 2rem;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.question-card {
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e0e0e0;
  transition: all 0.2s;
}

.question-card:hover {
  border-color: #2196F3;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.1);
}

.question-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  user-select: none;
}

.question-number {
  background: #2196F3;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.875rem;
}

.question-text {
  flex: 1;
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: #333;
}

.expand-icon {
  color: #666;
  font-size: 0.875rem;
}

.answer-content {
  padding: 1rem;
  padding-top: 0;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.answer-content p {
  margin: 0;
  color: #555;
  line-height: 1.6;
}
```

---

### 4. Обновить `StageDetail` компонент

**Удалить секцию Tips:**

```typescript
// ❌ Удалить эту секцию
<section className="stage-section tips">
  <h3>💡 Персональные советы</h3>
  <ul>
    {stage.tips.map((tip, index) => (
      <li key={index}>{tip}</li>
    ))}
  </ul>
</section>
```

**Добавить секцию Interview Questions:**

```typescript
// ✅ Добавить эту секцию
<InterviewQuestionsSection questions={stage.interviewQuestions} />
```

**Полный обновленный компонент:**

```typescript
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

      {/* ✅ Вопросы на собеседовании - НОВОЕ */}
      <InterviewQuestionsSection questions={stage.interviewQuestions} />
    </div>
  );
};
```

---

### 5. Обновить навигацию в главном компоненте

**Было:**

```typescript
<div className="roadmap-navigation">
  <button onClick={() => setActiveView('timeline')}>📅 Timeline</button>
  <button onClick={() => setActiveView('milestones')}>🏆 Вехи</button>
  <button onClick={() => setActiveView('certifications')}>📜 Сертификации</button>
  <button onClick={() => setActiveView('paths')}>🚀 Карьерные пути</button>
</div>

{activeView === 'timeline' && <RoadmapTimeline stages={roadmap.stages} />}
{activeView === 'milestones' && <MilestonesView milestones={roadmap.milestones} />}
{activeView === 'certifications' && <CertificationsView certifications={roadmap.certifications} />}
{activeView === 'paths' && <CareerPathsView careerPaths={roadmap.careerPaths} />}
```

**Стало (упрощенно):**

```typescript
// Просто показываем timeline с этапами
// Навигация не нужна, так как остался только один вид
<div className="roadmap-content">
  <RoadmapTimeline stages={roadmap.stages} />
</div>
```

---

### 6. Обновить заголовок страницы

**Убрать надпись "Career Roadmap":**

**Было:**

```typescript
<RoadmapOverviewComponent 
  overview={roadmap.overview} 
  profession={roadmap.profession} 
/>

// В компоненте:
<h1>🗺️ Career Roadmap: {profession}</h1>
```

**Стало:**

```typescript
<RoadmapOverviewComponent 
  overview={roadmap.overview} 
  profession={roadmap.profession} 
/>

// В компоненте:
<h1>🗺️ {profession}</h1>
```

**Добавить красивое выделение профессии:**

```typescript
<div className="roadmap-header">
  <div className="profession-badge">
    <span className="badge-icon">🎯</span>
    <span className="badge-text">Roadmap для</span>
  </div>
  <h1 className="profession-title">{profession}</h1>
</div>
```

**Стили:**

```css
.roadmap-header {
  text-align: center;
  margin-bottom: 2rem;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
}

.profession-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.badge-icon {
  font-size: 1.25rem;
}

.profession-title {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .profession-title {
    font-size: 1.75rem;
  }
}
```

---

## 📦 Миграция существующих данных

Если у вас есть сохраненные roadmap в локальном хранилище или БД:

```typescript
// Функция для миграции старого формата в новый
function migrateOldRoadmap(oldRoadmap: any): ProfessionRoadmap {
  return {
    profession: oldRoadmap.profession,
    overview: oldRoadmap.overview,
    stages: oldRoadmap.stages.map(stage => ({
      ...stage,
      interviewQuestions: [],  // Добавляем пустой массив
      // Удаляем tips если они есть
      tips: undefined,
    })),
    // Убираем старые поля
    milestones: undefined,
    certifications: undefined,
    careerPaths: undefined,
  };
}
```

---

## 🎨 Пример полного обновленного компонента

```typescript
// CompleteRoadmapView.tsx
import React, { useState, useEffect } from 'react';
import { generateRoadmap } from './api';
import { ProfessionRoadmap } from './types';

interface Props {
  professionTitle: string;
}

const CompleteRoadmapView: React.FC<Props> = ({ professionTitle }) => {
  const [roadmap, setRoadmap] = useState<ProfessionRoadmap | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadRoadmap();
  }, [professionTitle]);

  const loadRoadmap = async () => {
    setLoading(true);
    try {
      const data = await generateRoadmap(professionTitle);
      setRoadmap(data);
    } catch (error) {
      console.error('Error loading roadmap:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Генерация roadmap...</div>;
  }

  if (!roadmap) {
    return null;
  }

  return (
    <div className="complete-roadmap-view">
      {/* Красивый заголовок */}
      <div className="roadmap-header">
        <div className="profession-badge">
          <span className="badge-icon">🎯</span>
          <span className="badge-text">Roadmap для</span>
        </div>
        <h1 className="profession-title">{roadmap.profession}</h1>
      </div>

      {/* Обзор */}
      <RoadmapOverview overview={roadmap.overview} />

      {/* Этапы */}
      <div className="roadmap-content">
        <RoadmapTimeline stages={roadmap.stages} />
      </div>
    </div>
  );
};

export default CompleteRoadmapView;
```

---

## ✅ Checklist для фронтенд разработчика

- [ ] Обновить TypeScript интерфейсы (удалить старые, добавить `InterviewQuestion`)
- [ ] Удалить компоненты: `MilestonesView`, `CertificationsView`, `CareerPathsView`
- [ ] Создать компонент `InterviewQuestionsSection`
- [ ] Обновить `StageDetail` - удалить `tips`, добавить `interviewQuestions`
- [ ] Убрать лишнюю навигацию (оставить только Timeline)
- [ ] Обновить заголовок - убрать "Career Roadmap", добавить красивый badge
- [ ] Обновить стили для нового компонента вопросов
- [ ] Проверить миграцию старых данных (если есть)
- [ ] Протестировать отображение вопросов с раскрытием/скрытием ответов
- [ ] Проверить адаптивность на мобильных устройствах

---

## 🚀 Преимущества изменений

1. **Практичность** - вопросы на собеседование полезнее для пользователей, чем абстрактные вехи
2. **Упрощение** - меньше разделов = более простой и понятный интерфейс
3. **Фокус** - концентрация на главном: навыки, проекты, практика, подготовка к собеседованиям
4. **Читаемость** - улучшенное экранирование делает текст более читаемым

---

**Дата обновления**: 30 октября 2025  
**Версия API**: 2.0.0

