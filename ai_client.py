import logging
import httpx
from config import config

logger = logging.getLogger(__name__)

class AIClient:
    """Клиент для работы с OpenRouter API"""
    
    def __init__(self):
        self.client = httpx.Client(timeout=120.0)
        self.base_url = config.OPENROUTER_API_BASE
        self.model = config.MODEL_NAME
    
    def generate_epic(self, description: str, system_prompt: str) -> str | None:
        """
        Генерирует эпик на основе описания
        
        :param description: Описание задачи от пользователя
        :param system_prompt: Системный промпт
        :return: Сгенерированный эпик или None
        """
        try:
            logger.info("🤖 Генерация эпика...")
            
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
                    "stop": ["\n\n## 11", "## 11.", "Вот эпик:", "На основе описания:"],
                    "reasoning": {"enabled": True},
                },
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Ошибка API при генерации эпика: {response.status_code} - {response.text}")
                return None
            
            response_json = response.json()
            epic = response_json["choices"][0]["message"]["content"].strip()
            
            logger.info("✅ Эпик сгенерирован")
            return epic
            
        except Exception as e:
            logger.exception(f"❌ Ошибка при генерации эпика: {e}")
            return None
    
    def analyze_data(self, data_summary: str, system_prompt: str) -> str | None:
        """
        Анализирует данные и возвращает интерпретацию
        
        :param data_summary: Сводка данных
        :param system_prompt: Системный промпт
        :return: Анализ или None
        """
        try:
            logger.info("📊 Анализ данных...")
            
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers=config.OPENROUTER_HEADERS,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": data_summary},
                    ],
                    "temperature": config.AI_TEMPERATURE,
                    "max_tokens": config.AI_MAX_TOKENS_ANALYSIS,
                },
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Ошибка API при анализе данных: {response.status_code} - {response.text}")
                return None
            
            response_json = response.json()
            analysis = response_json["choices"][0]["message"]["content"].strip()
            
            logger.info("✅ Анализ завершён")
            return analysis
            
        except Exception as e:
            logger.exception(f"❌ Ошибка при анализе данных: {e}")
            return None
    
    def generate_presentation(self, epic_text: str, system_prompt: str) -> str | None:
        """
        Генерирует презентацию на основе эпика
        
        :param epic_text: Текст эпика
        :param system_prompt: Системный промпт
        :return: Текст презентации или None
        """
        try:
            logger.info("🎤 Генерация презентации...")
            
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                headers=config.OPENROUTER_HEADERS,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Создай презентацию на основе этого эпика:\n\n{epic_text}"},
                    ],
                    "temperature": config.AI_TEMPERATURE,
                    "max_tokens": 4000,
                    "stop": ["\n\nСлайд 11", "##", "Вот презентация:"],
                },
            )
            
            if response.status_code != 200:
                logger.error(f"❌ Ошибка API при генерации презентации: {response.status_code} - {response.text}")
                return None
            
            response_json = response.json()
            presentation = response_json["choices"][0]["message"]["content"].strip()
            
            logger.info("✅ Презентация сгенерирована")
            return presentation
            
        except Exception as e:
            logger.exception(f"❌ Ошибка при генерации презентации: {e}")
            return None
    
    def close(self):
        """Закрывает клиент"""
        self.client.close()