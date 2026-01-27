"""
Telegram бот для автоматического заполнения эпиков с помощью AI.
"""

import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)
from telegram.constants import ParseMode

from config import Config
from ai_handler import AIHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
WAITING_FOR_DESCRIPTION = 1

# Инициализация AI handler
ai_handler = AIHandler()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    welcome_message = """
👋 **Привет! Я бот для генерации эпиков.**

Я помогу тебе создать детальный эпик на основе краткого описания задачи.

**Как пользоваться:**
1. Отправь команду /new_epic
2. Опиши свою задачу в нескольких предложениях
3. Получи готовый эпик со всеми необходимыми секциями

**Доступные команды:**
/new_epic - Создать новый эпик
/help - Справка
/cancel - Отменить текущую операцию

Готов начать? Отправь /new_epic! 🚀
"""
    await update.message.reply_text(
        welcome_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    help_message = """
📖 **Справка по использованию бота**

**Команды:**
• /start - Приветственное сообщение
• /new_epic - Начать создание нового эпика
• /help - Показать эту справку
• /cancel - Отменить текущую операцию

**Пример использования:**

1️⃣ Отправь: `/new_epic`

2️⃣ Опиши задачу, например:
_"Добавить возможность экспорта отчетов в PDF формате с настройкой шаблонов"_

3️⃣ Получи готовый эпик с:
• Вводной и описанием проблемы
• User Stories
• Техническими требованиями
• MVP и планом реализации

**Важно:**
• Чем подробнее описание, тем лучше результат
• Укажи контекст, проблемы, цели
• Можно указать технические детали
"""
    await update.message.reply_text(
        help_message,
        parse_mode=ParseMode.MARKDOWN
    )


async def new_epic_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Начало создания нового эпика."""
    message = """
✍️ **Создание нового эпика**

Опиши задачу, для которой нужно создать эпик.

**Что указать:**
• Суть проблемы или задачи
• Текущую ситуацию
• Желаемый результат
• Технические детали (опционально)

**Пример:**
_"Нужно реализовать систему уведомлений для пользователей. Сейчас уведомления отправляются только по email, что недостаточно. Хотим добавить push-уведомления, SMS и Telegram. Система должна быть гибкой, с настройками приоритетов и каналов доставки."_

Жду твоего описания! Или /cancel для отмены.
"""
    await update.message.reply_text(
        message,
        parse_mode=ParseMode.MARKDOWN
    )
    return WAITING_FOR_DESCRIPTION


async def process_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка описания и генерация эпика."""
    user_description = update.message.text
    
    # Отправляем сообщение о начале генерации
    processing_message = await update.message.reply_text(
        "⏳ Генерирую эпик... Это может занять 30-60 секунд.",
        parse_mode=ParseMode.MARKDOWN
    )
    
    try:
        # Генерируем эпик
        epic_content = await ai_handler.generate_epic(user_description)
        
        if epic_content:
            # Удаляем сообщение о процессе
            await processing_message.delete()
            
            # Отправляем результат
            # Telegram ограничивает длину сообщения до 4096 символов
            await send_long_message(update, epic_content)
            
            logger.info(f"Эпик успешно отправлен пользователю {update.effective_user.id}")
        else:
            await processing_message.edit_text(
                "❌ Произошла ошибка при генерации эпика. Попробуй еще раз с /new_epic"
            )
            logger.error("Не удалось сгенерировать эпик")
    
    except Exception as e:
        logger.error(f"Ошибка при обработке описания: {str(e)}", exc_info=True)
        await processing_message.edit_text(
            "❌ Произошла ошибка. Попробуй еще раз позже или обратись к администратору."
        )
    
    return ConversationHandler.END


async def send_long_message(update: Update, text: str) -> None:
    """
    Отправляет длинное сообщение, разбивая его на части если нужно.
    
    Args:
        update: Update объект Telegram
        text: Текст для отправки
    """
    MAX_LENGTH = 4000  # Оставляем немного запаса от лимита 4096
    
    if len(text) <= MAX_LENGTH:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    else:
        # Разбиваем на части по секциям (по ##)
        parts = []
        current_part = ""
        
        for line in text.split('\n'):
            if len(current_part) + len(line) + 1 > MAX_LENGTH and current_part:
                parts.append(current_part)
                current_part = line + '\n'
            else:
                current_part += line + '\n'
        
        if current_part:
            parts.append(current_part)
        
        # Отправляем части
        for i, part in enumerate(parts, 1):
            header = f"📄 **Часть {i}/{len(parts)}**\n\n" if len(parts) > 1 else ""
            await update.message.reply_text(
                header + part,
                parse_mode=ParseMode.MARKDOWN
            )


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Отмена текущей операции."""
    await update.message.reply_text(
        "❌ Операция отменена. Используй /new_epic для создания нового эпика.",
        parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок."""
    logger.error(f"Ошибка при обработке обновления: {context.error}", exc_info=context.error)
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Произошла ошибка. Попробуй еще раз или обратись к администратору."
        )


def main() -> None:
    """Запуск бота."""
    logger.info("Запуск Telegram бота...")
    
    # Создаем приложение
    application = Application.builder().token(Config.TELEGRAM_TOKEN).build()
    
    # Conversation handler для создания эпика
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('new_epic', new_epic_command)],
        states={
            WAITING_FOR_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_description)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_command)],
    )
    
    # Добавляем обработчики
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(conv_handler)
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("Бот успешно запущен и готов к работе!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
