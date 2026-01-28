import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Настройки сервера
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 МБ
    
    # Render использует PORT из переменной окружения (по умолчанию 10000)
    PORT = int(os.environ.get('PORT', 10000))
    
    # ВАЖНО: Для Render должен быть 0.0.0.0
    HOST = '0.0.0.0'
    
    DEBUG = False

    # Настройки OpenRouter
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
    MODEL_NAME = os.getenv("MODEL_NAME", "deepseek/deepseek-v3.2")

    # Настройки AI
    AI_TEMPERATURE = 0.5
    AI_MAX_TOKENS_EPIC = 6000
    AI_MAX_TOKENS_ANALYSIS = 4000
    AI_MAX_TOKENS_COMPARISON = 5000

    # Настройки анализа данных
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 МБ
    CRITICAL_PERCENT_THRESHOLD = 40  # ← ИСПРАВЛЕНО: убран пробел

    # Заголовки для запросов к OpenRouter
    @property
    def OPENROUTER_HEADERS(self):
        return {
            "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": f"http://{self.HOST}:{self.PORT}",
            "X-Title": "ShezGard Bot",
        }

# Экземпляр конфигурации
config = Config()