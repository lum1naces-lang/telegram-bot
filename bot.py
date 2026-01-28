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
    
    # Сиси
    "сиси": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "сиси как дела": "Разве важно? Время идет, а я все так же свободна",
    "сиси что делаешь": "Отвечаю на твои глупые вопросы. А ты?",
    "сиси привет": "Ну, привет... опять ты появляешься.К сожалению",
    
    # Луми/создатель
    "кто такой этот ваш луми": "АХХ..луми..мой создатель",
    "луми": "Мой создатель, что о нем?",
    "создатель": "Луми создал меня, да-да.",
    
    # Дополнительные
    "бот": "Ну что тебе надо? "
    
    # Добавь свои слова ниже в таком же формате:
    # "твое слово": "твой ответ",
}

async def handle_message(update, context):
    """Обработка сообщений"""
    try:
        text = update.message.text.lower().strip()
        
        # Убираем знаки препинания для проверки
        clean_text = ''.join(char for char in text if char.isalnum() or char.isspace())
        
        # 1. Проверяем точное совпадение фразы (с пробелами)
        if text in RESPONSES:
            response = RESPONSES[text]
            await update.message.reply_text(
                response,
                parse_mode='Markdown' if text == "правила" else None
            )
            return
        
        # 2. Проверяем слова в очищенном тексте
        words = clean_text.split()
        for word in words:
            if word in RESPONSES:
                response = RESPONSES[word]
                await update.message.reply_text(
                    response,
                    parse_mode='Markdown' if word == "правила" else None
                )
                return
        
        # 3. Проверяем фразы из 2+ слов
        for phrase, response in RESPONSES.items():
            if ' ' in phrase:  # Если фраза из нескольких слов
                if phrase in clean_text:
                    await update.message.reply_text(
                        response,
                        parse_mode='Markdown' if phrase == "правила" else None
                    )
                    return
                    
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
        "Доступные команды:\n"
        "• правила - ссылка на правила\n"
        "• привет - поздороваться\n"
        "• сиси ... - вопросы для Сиси\n"
        "• луми / создатель - про создателя\n"
        "• бот - проверить работу\n"
        "• помощь / help - справка\n\n"
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
