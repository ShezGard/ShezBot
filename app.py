from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from config import config
from ai_client import AIClient
from data_analyzer import (
    analyze_csv,
    format_data_summary,
    compare_periods,
)
from utils import get_startup_message, validate_description, validate_file_size, logger
from prompts import (
    SYSTEM_PROMPT_EPIC,
    SYSTEM_PROMPT_ANALYSIS,
    SYSTEM_PROMPT_COMPARISON,
    SYSTEM_PROMPT_PRESENTATION
)

# Инициализация приложения
app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Инициализация клиента AI
ai_client = AIClient()

# ==================== Роуты ====================

@app.route("/")
def index():
    """Главная страница"""
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate_epic():
    """Генерация эпика по описанию"""
    data = request.get_json()
    if not data or "description" not in data:
        return jsonify({"error": "Отсутствует поле 'description'"}), 400
    
    description = data["description"].strip()
    
    # Валидация
    is_valid, error_message = validate_description(description)
    if not is_valid:
        return jsonify({"error": error_message}), 400
    
    logger.info("=" * 60)
    logger.info(f"📨 Новый запрос на генерацию эпика")
    logger.info(f"📝 Описание: {description[:100]}...")
    logger.info("=" * 60)
    
    # Генерация эпика
    epic = ai_client.generate_epic(description, SYSTEM_PROMPT_EPIC)
    
    if not epic:
        logger.error("❌ Не удалось сгенерировать эпик")
        return jsonify({"error": "Ошибка генерации эпика. Проверь консоль сервера для деталей."}), 500
    
    logger.info("✅ Отправляю эпик пользователю")
    return jsonify({"epic": epic})

@app.route("/api/upload", methods=["POST"])
def upload_file():
    """Обработка загрузки CSV/XLSX файла"""
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
        
        # Проверка размера
        file.seek(0, 2)  # Перемещаемся в конец файла
        file_size = file.tell()
        file.seek(0)  # Возвращаемся в начало
        
        is_valid, error_message = validate_file_size(file_size)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
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
        data_summary = format_data_summary(analysis)
        
        # Запрос к AI для интерпретации
        ai_analysis = ai_client.analyze_data(data_summary, SYSTEM_PROMPT_ANALYSIS)
        
        return jsonify({
            "success": True,
            "analysis": analysis,
            "ai_analysis": ai_analysis,
            "data_summary": data_summary
        })
        
    except Exception as e:
        logger.exception(f"❌ Ошибка при загрузке файла: {e}")
        return jsonify({"error": f"Ошибка обработки файла: {str(e)}"}), 500

@app.route("/api/compare", methods=["POST"])
def compare_periods_api():
    """Сравнение двух периодов"""
    try:
        if 'file1' not in request.files or 'file2' not in request.files:
            return jsonify({"error": "Необходимо загрузить 2 файла"}), 400
        
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1.filename == '' or file2.filename == '':
            return jsonify({"error": "Имена файлов не должны быть пустыми"}), 400
        
        # Проверка расширений
        allowed_extensions = {'csv', 'xlsx', 'xls'}
        filename1 = file1.filename.lower()
        filename2 = file2.filename.lower()
        
        if not any(filename1.endswith(f'.{ext}') for ext in allowed_extensions):
            return jsonify({"error": f"Неподдерживаемый формат файла 1. Разрешены: .csv, .xlsx, .xls"}), 400
        
        if not any(filename2.endswith(f'.{ext}') for ext in allowed_extensions):
            return jsonify({"error": f"Неподдерживаемый формат файла 2. Разрешены: .csv, .xlsx, .xls"}), 400
        
        # Чтение файлов
        logger.info(f"📥 Загрузка файла 1: {file1.filename}")
        logger.info(f"📥 Загрузка файла 2: {file2.filename}")
        
        if filename1.endswith('.csv'):
            df1 = pd.read_csv(file1)
        else:
            df1 = pd.read_excel(file1)
        
        if filename2.endswith('.csv'):
            df2 = pd.read_csv(file2)
        else:
            df2 = pd.read_excel(file2)
        
        logger.info(f"✅ Загружено файл 1: {len(df1)} строк, {len(df1.columns)} колонок")
        logger.info(f"✅ Загружено файл 2: {len(df2)} строк, {len(df2.columns)} колонок")
        
        # Анализ каждого файла
        analysis1 = analyze_csv(df1)
        analysis2 = analyze_csv(df2)
        
        # Сравнение периодов
        comparison = compare_periods(analysis1, analysis2)
        
        # Формируем сводку для AI
        comparison_summary = format_comparison_summary(comparison, analysis1, analysis2)
        
        # Запрос к AI для интерпретации сравнения
        ai_comparison = ai_client.analyze_data(comparison_summary, SYSTEM_PROMPT_COMPARISON)
        
        return jsonify({
            "success": True,
            "comparison": comparison,
            "analysis1": analysis1,
            "analysis2": analysis2,
            "ai_comparison": ai_comparison,
            "filename1": file1.filename,
            "filename2": file2.filename
        })
        
    except Exception as e:
        logger.exception(f"❌ Ошибка при сравнении периодов: {e}")
        return jsonify({"error": f"Ошибка обработки файлов: {str(e)}"}), 500

@app.route("/api/presentation", methods=["POST"])
def generate_presentation():
    """Генерация презентации на основе эпика"""
    data = request.get_json()
    if not data or "epic" not in data:
        return jsonify({"error": "Отсутствует поле 'epic'"}), 400
    
    epic_text = data["epic"].strip()
    
    if len(epic_text) < 50:
        return jsonify({"error": "Эпик слишком короткий (минимум 50 символов)"}), 400
    
    logger.info("=" * 60)
    logger.info(f"🎤 Новый запрос на генерацию презентации")
    logger.info(f"📝 Длина эпика: {len(epic_text)} символов")
    logger.info("=" * 60)
    
    try:
        # Генерация презентации
        presentation = ai_client.generate_presentation(epic_text, SYSTEM_PROMPT_PRESENTATION)
        
        if not presentation:
            logger.error("❌ Не удалось сгенерировать презентацию")
            return jsonify({"error": "Ошибка генерации презентации. Проверь консоль сервера для деталей."}), 500
        
        # Парсим слайды для удобного отображения
        slides = _parse_presentation_to_slides(presentation)
        
        logger.info(f"✅ Сгенерировано {len(slides)} слайдов")
        logger.info("✅ Отправляю презентацию пользователю")
        
        return jsonify({
            "success": True,
            "presentation": presentation,
            "slides": slides
        })
        
    except Exception as e:
        logger.exception(f"❌ Ошибка при генерации презентации: {e}")
        return jsonify({"error": f"Ошибка генерации: {str(e)}"}), 500

def _parse_presentation_to_slides(presentation_text: str):
    """Парсит текст презентации на отдельные слайды"""
    slides = []
    lines = presentation_text.split('\n')
    current_slide = None
    
    for line in lines:
        line = line.strip()
        
        # Обнаружение начала нового слайда
        if line.startswith('Слайд ') and ':' in line:
            if current_slide:
                slides.append(current_slide)
            
            # Извлекаем номер и заголовок
            slide_header = line.split(':', 1)
            slide_number = slide_header[0].replace('Слайд ', '').strip()
            slide_title = slide_header[1].strip() if len(slide_header) > 1 else ''
            
            current_slide = {
                "number": slide_number,
                "title": slide_title,
                "content": []
            }
        elif current_slide and line:
            # Добавляем контент к текущему слайду
            current_slide["content"].append(line)
    
    # Добавляем последний слайд
    if current_slide:
        slides.append(current_slide)
    
    return slides

@app.route("/api/health")
def health():
    """Проверка здоровья сервиса"""
    return jsonify({
        "status": "ok",
        "message": "ShezGard Bot готов к работе!",
        "model": config.MODEL_NAME
    })

@app.errorhandler(404)
def not_found(e):
    """Обработка 404 ошибки"""
    return jsonify({"error": "Маршрут не найден"}), 404

@app.errorhandler(500)
def server_error(e):
    """Обработка 500 ошибки"""
    logger.exception("Внутренняя ошибка сервера")
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500

# ==================== Запуск ====================

def cleanup():
    """Очистка ресурсов при завершении"""
    logger.info("🧹 Очистка ресурсов...")
    ai_client.close()

if __name__ == "__main__":
    print(get_startup_message())
    
    # Render требует привязки к 0.0.0.0 и порту из переменной окружения
    host = '0.0.0.0'
    port = int(config.PORT)
    
    try:
        app.run(host=host, port=port, debug=config.DEBUG)
    except KeyboardInterrupt:
        print("\n🛑 Останавливаю сервер...")
    finally:
        cleanup()