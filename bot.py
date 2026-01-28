import os
import time
from telegram.ext import Application, MessageHandler, filters, CommandHandler

TOKEN = os.getenv("TOKEN")

print("=" * 50)
print("🤖 Бот запускается...")
time.sleep(2)
print("✅ Бот готов!")

# ⭐ Словарь слов и ответов (ДОБАВЛЯЙ СЮДА СВОИ СЛОВА)
RESPONSES = {
    # Основные
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "привет": "Привет!",
    
    # Сиси
    "сиси": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "сиси как дела": "Разве важно? Время идет, а я все так же свободна",
    "сиси что делаешь": "Отвечаю на твои глупые вопросы. А ты?",
    "сиси привет": "Ну, привет... опять ты появляешься. Что на этот раз?",
    
    # Луми/создатель
    "кто такой этот ваш луми": "АХХ..луми..мой создатель",
    "луми": "Мой создатель, что о нем?",
    "создатель": "Луми создал меня, да",
    
    # Дополнительные
    "бот": "Да, я здесь. Что нужно?",
    "help": "Пиши 'правила' или напиши что тебе нужно",
    "помощь": "Пиши 'правила' или напиши что тебе нужно",
    "спасибо": "Пожалуйста!",
    "пасиб": "Всегда рад помочь!",
}

async def handle_message(update, context):
    """Обработка сообщений - ТОЛЬКО отдельные слова/фразы"""
    try:
        text = update.message.text.lower().strip()
        
        # Убираем лишние пробелы
        text = ' '.join(text.split())
        
        # 1. Проверяем ТОЧНОЕ совпадение (фраза полностью)
        if text in RESPONSES:
            response = RESPONSES[text]
            await update.message.reply_text(
                response,
                parse_mode='Markdown' if text == "правила" else None
            )
            return
        
        # 2. Проверяем если это ОДНО слово
        words = text.split()
        if len(words) == 1:  # Только одно слово в сообщении
            word = words[0]
            if word in RESPONSES:
                response = RESPONSES[word]
                await update.message.reply_text(
                    response,
                    parse_mode='Markdown' if word == "правила" else None
                )
                return
        
        # 3. Если больше одного слова - НЕ реагируем
        # (чтобы не реагировал на "вот это БОТ" и т.д.)
        
    except Exception as e:
        print(f"Ошибка: {e}")

async def delete_message(update, context):
    """Удаление сообщения по команде !дел"""
    try:
        if update.message.reply_to_message:
            await update.message.reply_to_message.delete()
            await update.message.delete()
            print("🗑️ Удалил сообщение")
    except:
        pass

async def start(update, context):
    """Команда /start"""
    await update.message.reply_text(
        "✅ Бот работает!\n\n"
        "📌 Бот реагирует ТОЛЬКО на отдельные слова/фразы:\n"
        "• 'правила' ✅\n"
        "• 'привет' ✅\n"
        "• 'бот' ✅\n"
        "• 'вот это БОТ' ❌\n"
        "• 'супер правила' ❌\n\n"
        "• !дел - удалить сообщение (ответь на сообщение)\n\n"
        f"Всего команд: {len(RESPONSES)}"
    )

def main():
    """Запуск бота"""
    if not TOKEN:
        print("❌ Нет токена!")
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r'^!дел$') & filters.REPLY, delete_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"📦 Загружено {len(RESPONSES)} команд")
    print("🔥 Запускаю бота...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
