import os
import time
import subprocess
from telegram.ext import Application, MessageHandler, filters, CommandHandler

TOKEN = os.getenv("TOKEN")

print("=" * 50)
print("🔥 УБИВАЮ старые процессы...")

# Убиваем ВСЕ старые процессы Python
try:
    subprocess.run(["pkill", "-f", "python"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", "bot.py"], stderr=subprocess.DEVNULL)
except:
    pass

time.sleep(10)  # Ждем смерти старых
print("✅ Старые процессы убиты")
print("=" * 50)

RESPONSES = {
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "привет": "Привет!",
    "сиси": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "сиси как дела": "Разве важно? Время идет, а я все так же свободна",
    "сиси что делаешь": "Отвечаю на твои глупые вопросы. А ты?",
    "кто такой этот ваш луми": "АХХ..луми..мой создатель",
    "луми": "Мой создатель, что о нем?",
    "создатель": "Луми создал меня, да",
    "бот": "Да, я здесь. Что нужно?",
    "помощь": "Пиши 'правила' или напиши что тебе нужно",
    "спасибо": "Пожалуйста!",
}

async def handle_message(update, context):
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
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
            await update.message.delete()
            print("🗑️ Удалил сообщение")
        except:
            pass

async def start(update, context):
    await update.message.reply_text("✅ Бот работает! Пиши отдельные слова.")

def main():
    if not TOKEN:
        print("❌ Нет токена!")
        return
    
    print("🤖 Создаю нового бота...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^!дел$') & filters.REPLY, delete_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"📦 Загружено {len(RESPONSES)} команд")
    print("🔥 ЗАПУСКАЮ...")
    
    # Последняя попытка
    try:
        app.run_polling(
            drop_pending_updates=True,
            close_loop=False,
            stop_signals=[]  # Не реагировать на сигналы остановки
        )
    except Exception as e:
        print(f"💀 Ошибка: {e}")
        print("🔄 Перезапуск через 30 сек...")
        time.sleep(30)
        main()  # Рекурсивный перезапуск

if __name__ == "__main__":
    main()
