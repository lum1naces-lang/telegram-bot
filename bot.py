import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен из переменных окружения
TOKEN = os.getenv("TOKEN")

# Словарь ключевых слов и ответов
KEYWORDS_RESPONSES = {
    "Сиси привет": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "правило": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "бот": "Я туть",
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений с ключевыми словами"""
    try:
        if not update.message or not update.message.text:
            return
        
        message_text = update.message.text.lower().strip()
        
        # Проверяем ключевые слова - ТОЛЬКО целые слова!
        for keyword, response in KEYWORDS_RESPONSES.items():
            # Проверяем что это отдельное слово
            words = message_text.split()  # Разбиваем на слова
            if keyword in words:  # Ищем среди отдельных слов
                # Отправляем с кликабельной ссылкой
                await update.message.reply_text(
                    response, 
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                logger.info(f"Ответил на ключевое слово: {keyword}")
                return
                
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление сообщения по команде !дел"""
    try:
        # Проверяем, что это ответ на сообщение
        if not update.message.reply_to_message:
            await update.message.reply_text(
                "Ответьте командой `!дел` на сообщение, которое нужно удалить!"
            )
            return
        
        # Удаляем сообщение на которое ответили
        chat_id = update.message.chat_id
        message_id = update.message.reply_to_message.message_id
        
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )
        
        # Удаляем команду !дел тоже
        await update.message.delete()
        
        logger.info(f"Удалил сообщение {message_id}")
        
    except Exception as e:
        error_msg = str(e)
        if "message can't be deleted" in error_msg:
            await update.message.reply_text("Не могу удалить это сообщение!")
        else:
            logger.error(f"Ошибка удаления: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text(
        "Бот работает!\n\n"
        "Функции:\n"
        "• Отвечает на 'правила' со ссылкой\n"
        "• Удаляет сообщения по команде !дел\n\n"
        "Напишите 'правила' для получения ссылки."
    )

def main():
    """Основная функция запуска бота"""
    if not TOKEN:
        logger.error("Токен не найден!")
        return
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start_command))
    
    # Команда !дел (только если это ответ на сообщение)
    application.add_handler(MessageHandler(
        filters.Regex(r'^!дел$') & filters.REPLY,
        delete_message
    ))
    
    # Обработка обычных сообщений (правила, привет)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    # Запускаем бота
    logger.info("Бот запускается...")
    application.run_polling()

if __name__ == '__main__':
    main()
