from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
from config import config
from ai_client import AIClient
from data_analyzer import analyze_csv, format_data_summary
from utils import get_startup_message, validate_description, validate_file_size, logger
from prompts import SYSTEM_PROMPT_EPIC, SYSTEM_PROMPT_ANALYSIS

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
    
    if not data or "description" not in data:  # ← ИСПРАВЛЕНО: добавлено "data" после "not in"
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
<<<<<<< HEAD
    print(get_startup_message())
    
    try:
        app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
    except KeyboardInterrupt:
        print("\n🛑 Останавливаю сервер...")
    finally:
        cleanup()
=======
    # ВАЖНО: Используем порт из переменной окружения Render
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "=" * 60)
    print("🤖 ShezGard Bot — Веб-интерфейс")
    print("=" * 60)
    print(f"📍 Слушаю на: http://0.0.0.0:{port}")
    print(f"🧠 Модель: {ai_client.model}")
    print(f"📊 Поддержка вложенных тематик: ВКЛЮЧЕНА")
    print(f"📦 Макс. размер файла: 100 МБ")
    print("=" * 60 + "\n")
    
    # ЗАПУСК НА 0.0.0.0 + ПОРТ ИЗ ОКРУЖЕНИЯ (обязательно для Render!)
    app.run(host='0.0.0.0', port=port, debug=False)
>>>>>>> 3636a056258fbe65f6181c86705848d39aa5d548
