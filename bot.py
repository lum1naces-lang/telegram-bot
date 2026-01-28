import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")

KEYWORDS_RESPONSES = {
    "привет": "Привет!",
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "правило": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "бот": "Я туть",
}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message or not update.message.text:
            return
        
        message_text = update.message.text.lower().strip()
        words = message_text.split()
        
        for keyword, response in KEYWORDS_RESPONSES.items():
            if keyword in words:
                await update.message.reply_text(
                    response, 
                    parse_mode='Markdown',
                    disable_web_page_preview=False
                )
                return
                
    except Exception as e:
        logger.error(f"Ошибка: {e}")

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.message.reply_to_message:
            await update.message.reply_text("Ответьте `!дел` на сообщение")
            return
        
        await update.message.reply_to_message.delete()
        await update.message.delete()
        
    except Exception as e:
        logger.error(f"Ошибка удаления: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает! Напишите 'правила'")

def main():
    if not TOKEN:
        logger.error("Токен не найден!")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.Regex(r'^!дел$') & filters.REPLY, delete_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запускается...")
    # Ключевое исправление:
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

if __name__ == '__main__':
    main()
