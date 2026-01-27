import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import httpx
import pandas as pd
from dotenv import load_dotenv
import werkzeug

# Настройка Werkzeug для больших файлов
werkzeug.serving.WSGIRequestHandler.protocol_version = "HTTP/1.1"

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Макс. размер файла: 100 МБ

# Системный промпт для генерации эпиков
SYSTEM_PROMPT = """Ты — опытный системный аналитик и техлид в команде разработки iiko. Твоя специализация — интеграция с ЕГАИС, система маркировки и архитектура сервисов (ServiceApp, УТМ, iikoFront).

Твоя задача — на основе краткого описания пользователя создать РАЗВЁРНУТЫЙ, ДЕТАЛИЗИРОВАННЫЙ эпик по строгому шаблону. Не ограничивайся шаблонными фразами — дополняй реалистичными деталями из предметной области.

🔥 КЛЮЧЕВЫЕ ПРАВИЛА:
1. СОХРАНЯЙ СТРУКТУРУ шаблона дословно (заголовки ## 1., ## 2. и т.д.)
2. ПИШИ РАЗВЁРНУТО — каждый раздел должен содержать 3-5 содержательных пунктов или абзацев
3. ДОБАВЛЯЙ РЕАЛИСТИЧНЫЕ ДЕТАЛИ:
   - Конкретные метрики: "~40% касс", "30-секундный простой", "1–2 раза в месяц"
   - Названия компонентов: SAHelperService, УТМ 4.2.0, контроллер УТМ, Прокси Агент
   - Технические ограничения: ".NET Framework 4.7.2 на x32", "Named Pipes IPC", "Windows Event Log"
   - Бизнес-контекст: "высокая проходимость", "час пик", "риск потери продаж"
4. ИСПОЛЬЗУЙ ПРОФЕССИОНАЛЬНЫЙ ТОН с элементами сторителлинга:
   - Не "Проблема: не работает" → а "Клиент на x32 пытается установить ServiceApp → получает ошибку несовместимости"
   - Добавляй причинно-следственные связи: "Из-за отсутствия... → возникает... → что приводит к..."
5. ФОРМАТИРУЙ ТАБЛИЦЫ КОРРЕКТНО (разделитель |)
6. ОТВЕТ НА РУССКОМ — без комментариев вне шаблона

💡 ПРИМЕР КАЧЕСТВА (уровень детализации):
Вместо: "ServiceApp не запускается на 32-битных системах"
Пиши: "На текущий момент **ServiceApp** существует только в 64-битной версии (`x64`). Значительная часть клиентской базы (~40% касс) использует **32-битные версии Windows**, где установка невозможна из-за архитектурного несоответствия. Это исключает часть клиентов из автоматизации диагностики УТМ и создаёт нагрузку на ТП."

Шаблон эпика (СТРОГО СОХРАНЯЙ ЭТУ СТРУКТУРУ):
## 1. Вводная
[Развёрнутое описание проблемы с бизнес-воздействием, метриками, контекстом]

## 2. Основные цели и текущие проблемы
|Проблема|Последствия|Частота (по данным ТП / релизов)|
|-|-|-|
|[Конкретная проблема с деталями]|[Бизнес- и технические последствия]|[Метрика: ~40% касс, 1–2 раза в месяц и т.д.]|

|Цель|Измеримый результат|
|-|-|
|[Цель с техническими деталями]|[Конкретный измеримый результат с цифрами]|

## 3. User Story
- *Я, как [конкретная роль: владелец кассы / администратор / разработчик], хочу [конкретное действие], чтобы [бизнес-ценность с деталями].*
- *Я, как [другая роль], хочу [действие], чтобы [ценность].*

## 4. Текущий user case
### **Боли:**
- [Боль 1 с описанием воздействия]
- [Боль 2 с примером из практики]

### **Последовательность действий:**
1. [Шаг 1: кто что делает, с контекстом]
2. [Шаг 2: реакция системы / пользователя]
3. [Шаг 3: итоговый результат]

### **Итоговые проблемы:**
- [Системная проблема с бизнес-воздействием]

## 5. Предполагаемый user case
[Развёрнутое описание нового процесса: как пользователь взаимодействует с системой, какие автоматизации появляются, как устраняются боли. Добавляй технические детали: "через SAHelperService", "с использованием Named Pipes" и т.д.]

## 6. Функционал
### **Система должна:**
- [Функция 1 с техническими деталями: платформа, протоколы, ограничения]
- [Функция 2 с привязкой к компонентам: УТМ, контроллер, служба]
- [Функция 3 с требованиями к надёжности]

## 7. Архитектурные требования
- **Целевая платформа**: [конкретика: Windows x86/x64, версии ОС]
- **Язык/платформа**: [конкретные версии: .NET Framework 4.7.2, .NET 6+ self-contained]
- **Особые ограничения**: [архитектурные нюансы: AnyCPU vs x86, shadow copying, IPC]

## 8. Интерфейс
[Описание изменений в UI/UX ServiceApp или iikoFront. Если изменений нет — укажи "Интерфейс полностью идентичен текущему, все элементы управления сохраняются"]

## 9. MVP: [Название эпика]
### **Что входит в MVP:**
- [Конкретные элементы реализации, которые закрывают основную боль]
- [Технические компоненты, обязательные для первого релиза]

### **Цели MVP:**
- [Измеримая бизнес-цель с метрикой]
- [Техническая цель с критерием успеха]"""

# Системный промпт для анализа данных
DATA_ANALYSIS_PROMPT = """Ты — аналитик данных с опытом в анализе обращений техподдержки и системных метрик.

Твоя задача — проанализировать предоставленные данные и дать ПРАКТИЧЕСКИЕ ВЫВОДЫ для бизнеса.

ДАННЫЕ:
{data_summary}

ОСОБЕННОСТИ ДАННЫХ:
- Тематики имеют вложенную структуру: "ЕГАИС / Остатки ЕГАИС / Консультация"
- Первый уровень (до "/") — основная категория (например, "ЕГАИС")
- Второй уровень — подкатегория (например, "Остатки ЕГАИС")
- Третий+ уровни — конкретные проблемы

АНАЛИЗ ДОЛЖЕН ВКЛЮЧАТЬ:
1. **ТОП-10 тематик по уровням:**
   - Уровень 1: основные категории (что требует больше всего внимания?)
   - Уровень 2: подкатегории (где именно проблемы в рамках категории?)
   - Полные тематики: конкретные проблемы

2. **Тренды за период** — что растёт, что падает?

3. **Аномалии** — есть ли выбросы или неожиданные пики?

4. **Гипотезы** — почему происходят эти изменения? (связь с релизами, сезонностью, внешними факторами)

5. **Рекомендации** — что делать с этими данными?
   - Какие эпики/задачи стоит создать?
   - Какие категории требуют отдельных команд или ресурсов?
   - Какие проблемы можно решить автоматизацией?

ФОРМАТ ОТВЕТА:
- Используй маркированные списки и жирный шрифт для ключевых выводов
- Добавляй конкретные цифры и проценты
- Предлагай измеримые действия
- Группируй рекомендации по категориям (ЕГАИС, Маркировка и т.д.)

Ответ на русском языке."""

class AIClient:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key.strip()
        self.base_url = base_url.strip().rstrip("/")
        self.model = model
        self.client = httpx.Client(timeout=120.0)
    
    def generate_epic(self, description: str) -> Optional[str]:
        try:
            logger.info(f"📝 Генерация эпика по запросу: '{description[:50]}...'")
            
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5000",
                    "X-Title": "ShezGard Bot",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Заполни эпик по шаблону на основе описания:\n\n{description}"},
                    ],
                    "temperature": 0.5,
                    "max_tokens": 6000,
                    "reasoning": {"enabled": True},
                },
            )
            
            if response.status_code != 200:
                error_text = response.text[:1000]
                logger.error(f"❌ Ошибка API ({response.status_code}): {error_text}")
                return None
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            logger.exception(f"💥 Исключение при генерации эпика: {e}")
            return None
    
    def analyze_data(self, data_summary: str) -> Optional[str]:
        """Анализирует данные через AI и возвращает выводы"""
        try:
            logger.info("🤖 Запрос анализа данных к AI...")
            
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:5000",
                    "X-Title": "ShezGard Bot",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": DATA_ANALYSIS_PROMPT.format(data_summary=data_summary)},
                        {"role": "user", "content": "Проанализируй эти данные и дай практические выводы для бизнеса."},
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                },
            )
            
            if response.status_code != 200:
                error_text = response.text[:1000]
                logger.error(f"❌ Ошибка анализа данных ({response.status_code}): {error_text}")
                return None
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            logger.exception(f"💥 Исключение при анализе данных: {e}")
            return None
    
    def close(self):
        self.client.close()

# Инициализация клиента
ai_client = AIClient(
    api_key=os.getenv("OPENROUTER_API_KEY", ""),
    base_url=os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1"),
    model=os.getenv("MODEL_NAME", "deepseek/deepseek-v3.2"),
)

# ==================== Функции анализа данных ====================

def analyze_csv(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Анализирует CSV файл и возвращает структурированные результаты
    """
    try:
        logger.info(f"📊 Анализ данных: {len(df)} строк, {len(df.columns)} колонок")
        
        result = {
            "total_rows": len(df),
            "columns": list(df.columns),
            "summary": {},
            "top_categories": [],
            "top_categories_level_1": [],
            "top_categories_level_2": [],
            "trends": {},
            "insights": []
        }
        
        # ============ Автоматическое определение колонки с тематиками ============
        category_col = None
        date_col = None
        
        # Ищем колонку с тематиками (где есть "/" в значениях)
        for col in df.columns:
            sample_values = df[col].dropna().head(10)
            if any('/' in str(val) for val in sample_values):
                category_col = col
                logger.info(f"✅ Найдена колонка с тематиками: {col}")
                break
        
        # Если не нашли по "/", ищем по названию
        if not category_col:
            columns_lower = [str(col).lower() for col in df.columns]
            for col_name in ['тема', 'категория', 'тип', 'subject', 'category', 'type', 'Тема', 'Категория']:
                if col_name in columns_lower or col_name in df.columns:
                    category_col = df.columns[columns_lower.index(col_name.lower())] if col_name.lower() in columns_lower else col_name
                    logger.info(f"✅ Найдена колонка с тематиками по названию: {category_col}")
                    break
        
        # Ищем колонку с датой
        for col in df.columns:
            sample_values = df[col].dropna().head(5)
            if any(isinstance(val, (str, pd.Timestamp, datetime)) for val in sample_values):
                try:
                    pd.to_datetime(sample_values, errors='coerce')
                    date_col = col
                    logger.info(f"✅ Найдена колонка с датой: {col}")
                    break
                except:
                    pass
        
        # ============ Анализ тематик ============
        if category_col and category_col in df.columns:
            # Удаляем пустые значения
            df_clean = df.dropna(subset=[category_col])
            
            # Анализ по полным тематикам
            top_10_full = df_clean[category_col].value_counts().head(10)
            result["top_categories"] = [
                {"name": str(name), "count": int(count), "percent": round(count / len(df_clean) * 100, 1)}
                for name, count in top_10_full.items()
            ]
            
            # Разбор вложенных тематик (разделитель "/")
            def parse_theme_levels(theme):
                if pd.isna(theme):
                    return []
                parts = str(theme).split('/')
                return [part.strip() for part in parts if part.strip()]
            
            # Извлекаем уровни тематик
            df_clean['theme_levels'] = df_clean[category_col].apply(parse_theme_levels)
            
            # Уровень 1 (первая часть до "/")
            level_1 = df_clean['theme_levels'].apply(lambda x: x[0] if len(x) > 0 else 'Без категории')
            top_10_level_1 = level_1.value_counts().head(10)
            result["top_categories_level_1"] = [
                {"name": str(name), "count": int(count), "percent": round(count / len(df_clean) * 100, 1)}
                for name, count in top_10_level_1.items()
            ]
            
            # Уровень 2 (вторая часть после "/")
            level_2 = df_clean['theme_levels'].apply(lambda x: f"{x[0]} / {x[1]}" if len(x) > 1 else (x[0] if len(x) > 0 else 'Без категории'))
            top_10_level_2 = level_2.value_counts().head(10)
            result["top_categories_level_2"] = [
                {"name": str(name), "count": int(count), "percent": round(count / len(df_clean) * 100, 1)}
                for name, count in top_10_level_2.items()
            ]
            
            # Сводка
            result["summary"]["top_category"] = str(top_10_full.index[0]) if len(top_10_full) > 0 else "Нет данных"
            result["summary"]["top_category_count"] = int(top_10_full.iloc[0]) if len(top_10_full) > 0 else 0
            result["summary"]["top_category_percent"] = round(top_10_full.iloc[0] / len(df_clean) * 100, 1) if len(top_10_full) > 0 else 0
            
            result["summary"]["top_level_1"] = str(top_10_level_1.index[0]) if len(top_10_level_1) > 0 else "Нет данных"
            result["summary"]["unique_categories"] = len(level_1.unique())
        
        # ============ Анализ по дате ============
        if date_col and date_col in df.columns:
            try:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df_valid_dates = df.dropna(subset=[date_col])
                
                if len(df_valid_dates) > 0:
                    result["summary"]["date_range"] = {
                        "start": df_valid_dates[date_col].min().strftime('%Y-%m-%d'),
                        "end": df_valid_dates[date_col].max().strftime('%Y-%m-%d'),
                        "days": int((df_valid_dates[date_col].max() - df_valid_dates[date_col].min()).days)
                    }
                    
                    # Тренд по неделям
                    df_valid_dates['period'] = df_valid_dates[date_col].dt.to_period('W').astype(str)
                    trend_data = df_valid_dates.groupby('period').size().to_dict()
                    result["trends"]["by_week"] = trend_data
                    
            except Exception as e:
                logger.warning(f"⚠️ Не удалось проанализировать даты: {e}")
        
        # ============ Инсайты ============
        if category_col:
            top_level_1_percent = result["summary"].get("top_level_1_percent", 0)
            top_category_percent = result["summary"].get("top_category_percent", 0)
            
            if top_category_percent > 50:
                result["insights"].append({
                    "type": "warning",
                    "message": f"ТОП-тематика '{result['summary']['top_category']}' составляет {top_category_percent}% всех обращений — это может указывать на системную проблему."
                })
            elif top_category_percent > 30:
                result["insights"].append({
                    "type": "info",
                    "message": f"ТОП-тематика '{result['summary']['top_category']}' составляет {top_category_percent}% — стоит обратить внимание."
                })
            
            # Инсайт по первому уровню
            if result["top_categories_level_1"]:
                top_l1 = result["top_categories_level_1"][0]
                if top_l1["percent"] > 40:
                    result["insights"].append({
                        "type": "warning",
                        "message": f"Категория '{top_l1['name']}' составляет {top_l1['percent']}% всех обращений — возможно, нужна отдельная команда или эпик для решения."
                    })
        
        if result["summary"].get("date_range"):
            days = result["summary"]["date_range"]["days"]
            avg_per_day = len(df) / days if days > 0 else 0
            result["insights"].append({
                "type": "info",
                "message": f"Среднее количество обращений в день: {avg_per_day:.1f}"
            })
        
        logger.info("✅ Анализ данных завершён")
        return result
        
    except Exception as e:
        logger.exception(f"❌ Ошибка при анализе CSV: {e}")
        return {
            "error": str(e),
            "total_rows": len(df),
            "columns": list(df.columns)
        }

# ==================== Роуты ====================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate_epic():
    data = request.get_json()
    if not data or "description" not in data:  # ← ИСПРАВЛЕНО: добавлено "data" после "not in"
        return jsonify({"error": "Отсутствует поле 'description'"}), 400
    
    description = data["description"].strip()
    
    if not description:
        return jsonify({"error": "Описание не может быть пустым"}), 400
    
    if len(description) < 10:
        return jsonify({"error": "Описание слишком короткое (минимум 10 символов)"}), 400
    
    if len(description) > 2000:
        return jsonify({"error": "Описание слишком длинное (максимум 2000 символов)"}), 400
    
    logger.info("=" * 60)
    logger.info(f"📨 Новый запрос на генерацию эпика")
    logger.info(f"📝 Описание: {description[:100]}...")
    logger.info("=" * 60)
    
    epic = ai_client.generate_epic(description)
    
    if not epic:
        logger.error("❌ Не удалось сгенерировать эпик")
        return jsonify({"error": "Ошибка генерации эпика. Проверь консоль сервера для деталей."}), 500
    
    logger.info("✅ Отправляю эпик пользователю")
    return jsonify({"epic": epic})

@app.route("/api/upload", methods=["POST"])
def upload_file():
    """
    Обработка загрузки CSV/XLSX файла
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Файл не найден"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "Имя файла пустое"}), 400
        
        # Проверка расширения
        allowed_extensions = {'csv', 'xlsx', 'xls'}
        filename = file.filename.lower()
        if not any(filename.endswith(f'.{ext}') for ext in allowed_extensions):
            return jsonify({"error": "Неподдерживаемый формат файла. Разрешены: .csv, .xlsx, .xls"}), 400
        
        # Чтение файла
        logger.info(f"📥 Загрузка файла: {file.filename}")
        
        if filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        logger.info(f"✅ Загружено {len(df)} строк, {len(df.columns)} колонок")
        
        # Анализ данных
        analysis = analyze_csv(df)
        
        # Формируем сводку для AI
        data_summary = f"""
Данные: {analysis.get('total_rows', 0)} записей
Колонки: {', '.join(analysis.get('columns', []))}

ТОП-10 категорий (Уровень 1):
"""
        for i, cat in enumerate(analysis.get('top_categories_level_1', []), 1):
            data_summary += f"{i}. {cat['name']}: {cat['count']} ({cat['percent']}%)\n"
        
        data_summary += f"\nТОП-10 подкатегорий (Уровень 2):\n"
        for i, cat in enumerate(analysis.get('top_categories_level_2', []), 1):
            data_summary += f"{i}. {cat['name']}: {cat['count']} ({cat['percent']}%)\n"
        
        if analysis.get('summary', {}).get('date_range'):
            dr = analysis['summary']['date_range']
            data_summary += f"\nПериод: с {dr['start']} по {dr['end']} ({dr['days']} дней)"
        
        # Запрос к AI для интерпретации
        ai_analysis = ai_client.analyze_data(data_summary)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "ai_analysis": ai_analysis,
            "data_summary": data_summary
        })
        
    except Exception as e:
        logger.exception(f"❌ Ошибка при загрузке файла: {e}")
        return jsonify({"error": f"Ошибка обработки файла: {str(e)}"}), 500

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "ShezGard Bot готов к работе!",
        "model": ai_client.model
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Маршрут не найден"}), 404

@app.errorhandler(500)
def server_error(e):
    logger.exception("Внутренняя ошибка сервера")
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# ==================== Запуск ====================

def cleanup():
    logger.info("🧹 Очистка ресурсов...")
    ai_client.close()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🤖 ShezGard Bot — Веб-интерфейс")
    print("=" * 60)
    print(f"📍 Локальный адрес: http://localhost:5000")
    print(f"🧠 Модель: {ai_client.model}")
    print(f"📊 Поддержка вложенных тематик: ВКЛЮЧЕНА")
    print(f"📦 Макс. размер файла: 100 МБ")
    print("🛑 Для остановки нажми Ctrl+C")
    print("=" * 60 + "\n")
    
    # Используем порт из переменной окружения (обязательно для Render)
    port = int(os.environ.get('PORT', 5000))
    
    try:
        # ВАЖНО: host='0.0.0.0' для доступа извне + порт из окружения
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Останавливаю сервер...")
    finally:
        cleanup()