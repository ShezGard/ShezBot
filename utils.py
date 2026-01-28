import logging
from config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_startup_message() -> str:
    """Возвращает красивое сообщение при запуске"""
    # Собираем сообщение по частям — избегаем проблем с эмодзи в f-строках
    border = "=" * 60
    return (
        f"{border}\n"
        "🤖 ShezGard Bot — Веб-интерфейс\n"
        f"{border}\n"
        f"📍 Слушаю на: http://{config.HOST}:{config.PORT}\n"
        f"🧠 Модель: {config.MODEL_NAME}\n"
        "📊 Поддержка вложенных тематик: ВКЛЮЧЕНА\n"
        f"📦 Макс. размер файла: {config.MAX_FILE_SIZE / 1024 / 1024:.0f} МБ\n"
        "🛑 Для остановки нажми Ctrl+C\n"
        f"{border}\n"
    )

def validate_description(description: str) -> tuple[bool, str]:
    """Валидация описания для генерации эпика"""
    if not description:
        return False, "Описание не может быть пустым"
    
    if len(description) < 10:
        return False, "Описание слишком короткое (минимум 10 символов)"
    
    if len(description) > 2000:
        return False, "Описание слишком длинное (максимум 2000 символов)"
    
    return True, ""

def validate_file_size(file_size: int) -> tuple[bool, str]:
    """Валидация размера файла"""
    if file_size > config.MAX_FILE_SIZE:
        return False, f"Файл слишком большой! Максимальный размер: {config.MAX_FILE_SIZE / 1024 / 1024:.0f} МБ. Текущий размер: {file_size / 1024 / 1024:.2f} МБ"
    
    return True, ""