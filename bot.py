import os
import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler

TOKEN = os.getenv("TOKEN")

print("=" * 50)
print("🤖 НОВЫЙ бот запускается...")
time.sleep(3)
print("✅ Начинаю работу")

RESPONSES = {
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "сиси": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "сиси как дела": "Разве важно? Время идет, а я все так же свободна",
    "сиси что делаешь": "Отвечаю на твои глупые вопросы. А ты?",
    "кто такой этот ваш луми": "АХХ..луми..мой создатель",
    "луми": "Мхх..",
    "бот": "Ну чего тебе?",
}

async def handle_message(update, context):
    """Обработка сообщений - ТОЛЬКО отдельные слова"""
    text = update.message.text.lower().strip()
    
    # ТОЛЬКО точное совпадение
    if text in RESPONSES:
        response = RESPONSES[text]
        await update.message.reply_text(
            response,
            parse_mode='Markdown' if text == "правила" else None
        )
        return

async def delete_message(update, context):
    """Удаление сообщения по команде !дел"""
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
            await update.message.delete()
            print("🗑️ Удалил сообщение")
        except Exception as e:
            print(f"Ошибка удаления: {e}")
            try:
                await update.message.reply_text("❌ Не могу удалить!")
            except:
                pass

async def start(update, context):
    """Команда /start"""
    await update.message.reply_text("Работаю")

def main():
    """Запуск бота"""
    if not TOKEN:
        print("❌ Нет токена!")
        return
    
    print(f"📦 Загружено {len(RESPONSES)} команд")
    
    app = Application.builder().token(TOKEN).build()
    
    # 1. Команда /start
    app.add_handler(CommandHandler("start", start))
    
    # 2. Команда !дел (только если ответ на сообщение)
    app.add_handler(MessageHandler(
        filters.Regex(r'^!дел$') & filters.REPLY,
        delete_message
    ))
    
    # 3. Обычные сообщения
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    print("🔥 БОТ ЗАПУЩЕН И РАБОТАЕТ!")
    print("Ожидаю сообщения...")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
