import logging
import httpx
from config import config

logger = logging.getLogger(__name__)

class AIClient:
    """Клиент для работы с OpenRouter AI"""
    
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_API_BASE
        self.model = config.MODEL_NAME
        self.client = httpx.Client(timeout=120.0)
    
    def generate_epic(self, description: str, system_prompt: str) -> str | None:
        """Генерирует эпик по описанию"""
        try:
            logger.info(f"📝 Генерация эпика: '{description[:50]}...'")
            
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers=config.OPENROUTER_HEADERS,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Заполни эпик по шаблону на основе описания:\n\n{description}"},
                    ],
                    "temperature": config.AI_TEMPERATURE,
                    "max_tokens": config.AI_MAX_TOKENS_EPIC,
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
    
    def analyze_data(self, data_summary: str, system_prompt: str) -> str | None:
        """Анализирует данные через AI и возвращает выводы"""
        try:
            logger.info("🤖 Запрос анализа данных к AI...")
            
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers=config.OPENROUTER_HEADERS,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt.format(data_summary=data_summary)},
                        {"role": "user", "content": "Проанализируй эти данные и дай стратегический отчёт для руководителя."},
                    ],
                    "temperature": config.AI_TEMPERATURE,
                    "max_tokens": config.AI_MAX_TOKENS_ANALYSIS,
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
        """Закрывает клиент"""
        self.client.close()