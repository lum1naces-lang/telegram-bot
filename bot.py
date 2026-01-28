import os
from telegram.ext import Application, CommandHandler, MessageHandler, filters

TOKEN = os.getenv("TOKEN")

KEYWORDS_RESPONSES = {
    "привет": "Привет!",
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
}

async def handle_message(update, context):
    if update.message and update.message.text:
        text = update.message.text.lower()
        if "правила" in text:
            await update.message.reply_text(
                KEYWORDS_RESPONSES["правила"],
                parse_mode='Markdown'
            )
        elif "привет" in text:
            await update.message.reply_text("Привет!")

async def delete_message(update, context):
    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
            await update.message.delete()
        except:
            pass

def main():
    if not TOKEN:
        return
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u,c: u.message.reply_text("Бот работает!")))
    app.add_handler(MessageHandler(filters.Regex(r'^!дел$') & filters.REPLY, delete_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
