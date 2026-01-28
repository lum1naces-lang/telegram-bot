import os
import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler

TOKEN = os.getenv("TOKEN")

print("=" * 50)
print("Бот запускается...")
print(f"Токен: {TOKEN[:10]}..." if TOKEN else "Токен не найден!")
print("=" * 50)

time.sleep(2)

# ⭐⭐ СЮДА ДОБАВЛЯЙТЕ СВОИ СЛОВА И ОТВЕТЫ ⭐⭐
RESPONSES = {
    # Основные команды
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    
    # Для Сиси
    "сиси": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "сиси привет": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "сиси как дела": "Разве важно? Время идет, а я все так же свободна",
    "сиси как дела?": "Разве важно? Время идет, а я все так же свободна",
    "сиси что делаешь": "Отвечаю на твои глупые вопросы. А ты?",
    "сиси ты тут": "К сожалению, да. Что нужно?",
    "кто такой этот ваш луми": "Ахх..луми, мой дорогой создатель",
    # Добавьте свои слова ниже в том же формате:
    # "ваше слово": "ваш ответ",
}

async def handle_message(update, context):
    text = update.message.text.lower().strip()
    
    # 1. Сначала проверяем точные совпадения из словаря
    if text in RESPONSES:
        response = RESPONSES[text]
        await update.message.reply_text(
            response,
            parse_mode='Markdown' if text == "правила" else None
        )
        return
    
    # 2. Проверяем ключевые слова в сообщении
    for keyword, response in RESPONSES.items():
        # Если ключевое слово содержится в тексте
        if keyword in text:
            await update.message.reply_text(
                response,
                parse_mode='Markdown' if keyword == "правила" else None
            )
            return

async def delete_message(update, context):
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
            await update.message.delete()
            print(f"Удалил сообщение")
        except:
            await update.message.reply_text("Не могу удалить!")

async def start(update, context):
    await update.message.reply_text("Бот работает! Пишите 'правила' или 'сиси как дела'")

def main():
    if not TOKEN:
        print("ERROR: Нет токена!")
        return
    
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^!дел$') & filters.REPLY, delete_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"✅ Бот запущен! Загружено {len(RESPONSES)} команд")
    print("Ожидаю сообщения...")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
