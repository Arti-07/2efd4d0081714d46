# 📄 PDF Export для Career Roadmap

## ✅ Исправление: Invalid \escape ошибка

### Проблема
```
Invalid \escape: line 272 column 152 (char 11515)
```

AI генерировал неправильно экранированные символы типа `\escape`, `\e`, `\.` и т.д.

### Решение
Улучшена функция `_sanitize_text_content` в агенте:
1. Сохраняем валидные escape-последовательности (`\"`, `\\`, `\n`, etc.)
2. Экранируем все оставшиеся backslash
3. Восстанавливаем валидные последовательности

Теперь JSON всегда валидный! ✅

---

## 📥 Экспорт Roadmap в PDF (Фронтенд)

### Вариант 1: Простой - react-to-pdf

**Установка:**
```bash
npm install react-to-pdf
# или
yarn add react-to-pdf
```

**Использование:**
```typescript
import { usePDF } from 'react-to-pdf';

const RoadmapView: React.FC = () => {
  const { toPDF, targetRef } = usePDF({
    filename: 'career-roadmap.pdf',
    page: { 
      margin: 20,
      format: 'a4'
    }
  });

  return (
    <div>
      <button onClick={() => toPDF()}>
        📄 Скачать PDF
      </button>
      
      <div ref={targetRef}>
        {/* Весь контент roadmap */}
        <RoadmapContent roadmap={roadmap} />
      </div>
    </div>
  );
};
```

---

### Вариант 2: Продвинутый - html2canvas + jsPDF

**Установка:**
```bash
npm install html2canvas jspdf
```

**Код:**
```typescript
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const exportToPDF = async () => {
  const element = document.getElementById('roadmap-content');
  if (!element) return;

  // Показываем loader
  setExporting(true);

  try {
    // Конвертируем в canvas
    const canvas = await html2canvas(element, {
      scale: 2, // Качество
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    });

    // Создаем PDF
    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    });

    // Размеры A4
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    
    // Размеры изображения
    const imgWidth = pdfWidth - 20; // Отступы
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let heightLeft = imgHeight;
    let position = 10;

    // Добавляем первую страницу
    pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
    heightLeft -= pdfHeight;

    // Добавляем остальные страницы если контент больше одной
    while (heightLeft > 0) {
      position = heightLeft - imgHeight + 10;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;
    }

    // Скачиваем
    pdf.save('career-roadmap.pdf');
  } catch (error) {
    console.error('Error exporting PDF:', error);
    alert('Ошибка при экспорте PDF');
  } finally {
    setExporting(false);
  }
};
```

**Компонент с кнопкой:**
```typescript
const RoadmapView: React.FC<{ roadmap: ProfessionRoadmap }> = ({ roadmap }) => {
  const [exporting, setExporting] = useState(false);

  return (
    <div className="roadmap-container">
      <div className="roadmap-actions">
        <button 
          onClick={exportToPDF}
          disabled={exporting}
          className="btn-export-pdf"
        >
          {exporting ? (
            <>⏳ Экспортируем...</>
          ) : (
            <>📄 Скачать PDF</>
          )}
        </button>
      </div>

      <div id="roadmap-content" className="roadmap-content">
        {/* Весь контент roadmap */}
        <RoadmapHeader roadmap={roadmap} />
        <RoadmapOverview overview={roadmap.overview} />
        
        {roadmap.stages.map(stage => (
          <StageDetail key={stage.id} stage={stage} />
        ))}
      </div>
    </div>
  );
};
```

---

### Вариант 3: Чистый jsPDF (без скриншота)

Для более красивого PDF можно рендерить контент напрямую:

```typescript
import jsPDF from 'jspdf';

const exportToPDF = (roadmap: ProfessionRoadmap) => {
  const pdf = new jsPDF();
  let y = 20;
  const lineHeight = 7;
  const pageHeight = pdf.internal.pageSize.getHeight();

  // Заголовок
  pdf.setFontSize(20);
  pdf.setFont('helvetica', 'bold');
  pdf.text(roadmap.profession, 20, y);
  y += lineHeight * 2;

  // Обзор
  pdf.setFontSize(12);
  pdf.setFont('helvetica', 'normal');
  const splitDescription = pdf.splitTextToSize(
    roadmap.overview.description, 
    170
  );
  pdf.text(splitDescription, 20, y);
  y += splitDescription.length * lineHeight + 10;

  // Этапы
  roadmap.stages.forEach((stage, index) => {
    // Проверка на новую страницу
    if (y > pageHeight - 40) {
      pdf.addPage();
      y = 20;
    }

    // Заголовок этапа
    pdf.setFontSize(16);
    pdf.setFont('helvetica', 'bold');
    pdf.text(`${index + 1}. ${stage.title}`, 20, y);
    y += lineHeight * 1.5;

    // Описание этапа
    pdf.setFontSize(10);
    pdf.setFont('helvetica', 'normal');
    const splitStage = pdf.splitTextToSize(stage.description, 170);
    pdf.text(splitStage, 20, y);
    y += splitStage.length * lineHeight + 5;

    // Цели
    pdf.setFont('helvetica', 'bold');
    pdf.text('Цели:', 25, y);
    y += lineHeight;
    pdf.setFont('helvetica', 'normal');
    stage.goals.forEach(goal => {
      if (y > pageHeight - 20) {
        pdf.addPage();
        y = 20;
      }
      const splitGoal = pdf.splitTextToSize(`• ${goal}`, 165);
      pdf.text(splitGoal, 30, y);
      y += splitGoal.length * lineHeight;
    });

    y += 5;
  });

  pdf.save(`roadmap-${roadmap.profession}.pdf`);
};
```

---

## 🎨 Стили для печати

Добавь CSS для оптимизации при экспорте:

```css
/* Стили для PDF экспорта */
@media print {
  .roadmap-actions,
  .roadmap-navigation {
    display: none !important;
  }

  .roadmap-content {
    width: 100%;
    max-width: 100%;
    padding: 20px;
  }

  .stage-detail {
    page-break-inside: avoid;
    margin-bottom: 20px;
  }

  .question-card {
    page-break-inside: avoid;
  }
}

/* Стили для экспорта через html2canvas */
.roadmap-content {
  background: white;
  padding: 40px;
  max-width: 210mm; /* A4 width */
}

.roadmap-content.exporting {
  /* Временно убираем тени и эффекты для лучшего качества */
  box-shadow: none !important;
}
```

---

## 🚀 Полный пример компонента

```typescript
import React, { useState } from 'react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { ProfessionRoadmap } from './types';

interface Props {
  roadmap: ProfessionRoadmap;
}

const RoadmapViewer: React.FC<Props> = ({ roadmap }) => {
  const [exporting, setExporting] = useState(false);

  const exportToPDF = async () => {
    const element = document.getElementById('roadmap-content');
    if (!element) return;

    setExporting(true);
    element.classList.add('exporting');

    try {
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        windowWidth: 1200,
        windowHeight: element.scrollHeight
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4'
      });

      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = pdfWidth - 20;
      const imgHeight = (canvas.height * imgWidth) / canvas.width;

      let heightLeft = imgHeight;
      let position = 10;

      pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
      heightLeft -= pdfHeight;

      while (heightLeft > 0) {
        position = heightLeft - imgHeight + 10;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
        heightLeft -= pdfHeight;
      }

      const filename = `roadmap-${roadmap.profession.replace(/\s+/g, '-')}.pdf`;
      pdf.save(filename);
      
      // Показать success notification
      alert('✅ PDF успешно скачан!');
    } catch (error) {
      console.error('Error exporting PDF:', error);
      alert('❌ Ошибка при экспорте PDF');
    } finally {
      setExporting(false);
      element.classList.remove('exporting');
    }
  };

  return (
    <div className="roadmap-viewer">
      <div className="roadmap-actions">
        <button 
          onClick={exportToPDF}
          disabled={exporting}
          className="btn-export-pdf"
        >
          {exporting ? (
            <>
              <span className="spinner">⏳</span>
              Экспортируем...
            </>
          ) : (
            <>
              <span className="icon">📄</span>
              Скачать PDF
            </>
          )}
        </button>
      </div>

      <div id="roadmap-content" className="roadmap-content">
        {/* Красивый заголовок */}
        <div className="roadmap-header-pdf">
          <div className="profession-badge">
            <span className="badge-icon">🎯</span>
            <span className="badge-text">Roadmap для</span>
          </div>
          <h1 className="profession-title">{roadmap.profession}</h1>
        </div>

        {/* Обзор */}
        <div className="roadmap-overview-pdf">
          <p className="description">{roadmap.overview.description}</p>
          <div className="overview-meta">
            <div className="meta-item">
              <strong>Длительность:</strong> {roadmap.overview.totalDuration}
            </div>
            <div className="meta-item">
              <strong>Ключевые навыки:</strong>
              <div className="skills-tags">
                {roadmap.overview.keySkills.map((skill, i) => (
                  <span key={i} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Этапы */}
        {roadmap.stages.map((stage, index) => (
          <div key={stage.id} className="stage-detail-pdf">
            <h2 className="stage-title">
              <span className="stage-number">{index + 1}</span>
              {stage.title}
              <span className="stage-level">{stage.level}</span>
            </h2>
            
            <p className="stage-description">{stage.description}</p>
            
            <div className="stage-section">
              <h3>🎯 Цели</h3>
              <ul>
                {stage.goals.map((goal, i) => (
                  <li key={i}>{goal}</li>
                ))}
              </ul>
            </div>

            <div className="stage-section">
              <h3>🔧 Навыки</h3>
              <div className="skills-grid-pdf">
                {stage.skills.map((skill, i) => (
                  <div key={i} className="skill-item-pdf">
                    <strong>{skill.name}</strong>
                    <p>{skill.description}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="stage-section">
              <h3>💬 Вопросы на собеседовании</h3>
              <div className="questions-pdf">
                {stage.interviewQuestions.map((qa, i) => (
                  <div key={i} className="question-item-pdf">
                    <div className="question-q">
                      <strong>Q{i + 1}:</strong> {qa.question}
                    </div>
                    <div className="question-a">
                      <strong>A:</strong> {qa.answer}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RoadmapViewer;
```

---

## 💅 CSS для PDF

```css
/* Кнопка экспорта */
.btn-export-pdf {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: transform 0.2s;
}

.btn-export-pdf:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-export-pdf:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Контент для PDF */
.roadmap-content {
  background: white;
  padding: 40px;
  max-width: 210mm;
  margin: 0 auto;
}

.roadmap-header-pdf {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 3px solid #667eea;
}

.stage-detail-pdf {
  margin-bottom: 40px;
  page-break-inside: avoid;
}

.stage-title {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #333;
  margin-bottom: 16px;
}

.stage-number {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.stage-level {
  background: #f0f0f0;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  margin-left: auto;
}

.questions-pdf {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.question-item-pdf {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.question-q {
  margin-bottom: 8px;
  color: #333;
}

.question-a {
  color: #555;
  padding-left: 20px;
}

/* Прячем при экспорте */
.exporting .roadmap-actions {
  display: none !important;
}
```

---

## ✅ Итого

1. **Исправлена ошибка экранирования** - JSON теперь всегда валидный
2. **PDF экспорт на фронтенде** - используй `html2canvas + jsPDF`
3. **Готовый код** - скопируй и адаптируй под свой проект
4. **Стили оптимизированы** - для красивого PDF

Все работает на фронте, бэку ничего делать не нужно! 🚀

