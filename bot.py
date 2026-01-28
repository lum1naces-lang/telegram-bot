import os
import logging
import signal
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получаем токен из переменных окружения
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    logger.error("Токен не найден! Укажите переменную окружения TOKEN")
    sys.exit(1)

# Словарь ключевых слов и ответов (ТОЛЬКО ОДНА КОМАНДА)
KEYWORDS_RESPONSES = {
    "привет": "Привет! Я бот этой группы. Рад вас видеть!"
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений с ключевыми словами"""
    try:
        if not update.message or not update.message.text:
            return
        
        message_text = update.message.text.lower().strip()
        
        # Ищем точные совпадения или частичные
        for keyword, response in KEYWORDS_RESPONSES.items():
            if keyword in message_text:
                await update.message.reply_text(response)
                logger.info(f"Ответил на ключевое слово: {keyword}")
                return
        
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    await update.message.reply_text(
        "🤖 Бот активирован!\n"
        "Я отвечаю на ключевые слова в группе.\n"
        "Попробуйте написать 'привет'"
    )

def signal_handler(signum, frame):
    """Обработка сигналов для graceful shutdown"""
    logger.info("Получен сигнал завершения...")
    sys.exit(0)

def main():
    """Основная функция запуска бота"""
    logger.info("Запуск бота...")
    
    # Регистрируем обработчик сигналов
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе!")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()
