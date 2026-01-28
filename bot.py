import os
import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler

TOKEN = os.getenv("TOKEN")

print("=" * 50)
print("Бот запускается...")
print(f"Токен: {TOKEN[:10]}..." if TOKEN else "Токен не найден!")
print("=" * 50)

# Даем время старому инстансу умереть
time.sleep(5)

async def handle_message(update, context):
    text = update.message.text.lower()
    words = text.split()
    
    if "правила" in words:
        await update.message.reply_text(
            "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
            parse_mode='Markdown'
        )
    elif "Сиси привет" in words:
        await update.message.reply_text("Ну, привет... опять ты появляешься. Что на этот раз?")

async def delete_message(update, context):
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
            await update.message.delete()
            print(f"Удалил сообщение")
        except:
            await update.message.reply_text("Не могу удалить!")

async def start(update, context):
    await update.message.reply_text("Бот работает! Команды: правила, привет, !дел")

def main():
    if not TOKEN:
        print("ERROR: Нет токена!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^!дел$') & filters.REPLY, delete_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен и работает!")
    print("Ожидаю сообщения...")
    
    # Ключевой параметр для избежания конфликтов
    app.run_polling(
        drop_pending_updates=True,
        close_loop=False,
        stop_signals=None
    )

if __name__ == "__main__":
    main()
