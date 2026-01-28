import os
import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler

TOKEN = os.getenv("TOKEN")

print("=" * 50)
print("Бот запускается...")
print("=" * 50)

time.sleep(2)

# Все команды бота
RESPONSES = {
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "привет": "Привет!",
    "сиси": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "сиси как дела": "Разве важно? Время идет, а я все так же свободна",
    "сиси что делаешь": "Отвечаю на твои глупые вопросы. А ты?",
}

async def handle_message(update, context):
    """Обработка сообщений"""
    try:
        text = update.message.text.lower().strip()
        
        # Проверяем точные совпадения
        for keyword, response in RESPONSES.items():
            if text == keyword or keyword in text:
                await update.message.reply_text(
                    response,
                    parse_mode='Markdown' if keyword == "правила" else None
                )
                return
    except:
        pass

async def delete_message(update, context):
    """Удаление по !дел"""
    try:
        if update.message.reply_to_message:
            await update.message.reply_to_message.delete()
            await update.message.delete()
            print("🗑️ Удалил сообщение")
    except:
        try:
            await update.message.reply_text("Не могу удалить!")
        except:
            pass

async def start(update, context):
    """Команда /start"""
    await update.message.reply_text("Бот работает! Пиши 'правила' или 'сиси как дела'")

def main():
    """Запуск бота"""
    if not TOKEN:
        print("ERROR: Нет токена!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    # Все обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^!дел$') & filters.REPLY, delete_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен и готов!")
    print("Ожидаю сообщения...")
    
    # Запускаем
    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message"]
    )

if __name__ == "__main__":
    main()
