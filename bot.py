import os
import time
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

print("=" * 50)
print("🤖 Бот запускается...")
time.sleep(3)
print("✅ Начинаю работу")

# ⚠️ ЗАМЕНИ НА СВОЙ TELEGRAM ID ⚠️
ADMIN_IDS = [123456789]  # Твой ID и других админов через запятую

# Хранилище варнов {user_id: {"warns": X, "limit": Y}}
user_warns = {}
DEFAULT_WARN_LIMIT = 3

# Словарь с вариантами ответов
RESPONSES = {
    "правила": "📜 С правилами можно ознакомиться [туть](https://telegra.ph/Rules-01-24-146)",
    "сиси": "Ну, привет... опять ты появляешься. Что на этот раз?",
    "сиси как дела": "Разве важно? Время идет, а я все так же свободна",
    "сиси что делаешь": "Отвечаю на твои глупые вопросы. А ты?",
    "кто такой этот ваш луми": "АХХ..луми..мой создатель",
    "луми": "Мхх..",
    "бот": "Ну чего тебе?",
}

def is_admin(user_id):
    """Проверяет, является ли пользователь админом"""
    return user_id in ADMIN_IDS

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений"""
    text = update.message.text.lower().strip()
    
    # Улучшенная проверка: реагирует если слово есть в сообщении
    for keyword, response in RESPONSES.items():
        # Для односложных слов проверяем точное вхождение
        if ' ' not in keyword:  # одно слово
            words = text.split()
            if keyword in words:
                await update.message.reply_text(
                    response,
                    parse_mode='Markdown' if keyword == "правила" else None
                )
                return
        else:  # фраза из нескольких слов
            if keyword in text:
                await update.message.reply_text(
                    response,
                    parse_mode='Markdown' if keyword == "правила" else None
                )
                return

async def точка_дел(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .дел - удалить сообщение (только для админов)"""
    if not is_admin(update.message.from_user.id):
        await update.message.delete()  # Удаляем команду неадмина
        return
    
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

async def точка_пинг(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .пинг - проверка пинга (только для админов)"""
    if not is_admin(update.message.from_user.id):
        await update.message.delete()  # Удаляем команду неадмина
        return
    
    start_time = time.time()
    sent_message = await update.message.reply_text("🏓 Измеряю пинг...")
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 2)
    await sent_message.edit_text(f"🏓 Пинг бота: {ping_ms}мс")

async def точка_варн(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .варн - выдать предупреждение (только для админов)"""
    if not is_admin(update.message.from_user.id):
        await update.message.delete()  # Удаляем команду неадмина
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Ответьте на сообщение пользователя!")
        return
    
    user = update.message.reply_to_message.from_user
    user_id = user.id
    
    # Инициализируем если нет
    if user_id not in user_warns:
        user_warns[user_id] = {"warns": 0, "limit": DEFAULT_WARN_LIMIT}
    
    user_warns[user_id]["warns"] += 1
    warns = user_warns[user_id]["warns"]
    limit = user_warns[user_id]["limit"]
    
    await update.message.reply_text(
        f"⚠️ {user.first_name} получил предупреждение!\n"
        f"Варны: {warns}/{limit}"
    )
    
    # Если достиг лимита
    if warns >= limit:
        try:
            # Мут на 10 часов
            mute_until = datetime.now() + timedelta(hours=10)
            await context.bot.restrict_chat_member(
                chat_id=update.message.chat_id,
                user_id=user_id,
                until_date=mute_until,
                permissions=ChatPermissions(
                    can_send_messages=False,
                    can_send_media_messages=False,
                    can_send_polls=False,
                    can_send_other_messages=False,
                    can_add_web_page_previews=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False
                )
            )
            await update.message.reply_text(
                f"🚫 {user.first_name} получил мут на 10 часов за {limit} предупреждений!"
            )
            user_warns[user_id]["warns"] = 0  # Сброс после мута
        except Exception as e:
            await update.message.reply_text(f"❌ Не смог замутить: {e}")

async def точка_варнлимит(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .варнлимит - изменить лимит варнов (только для админов)"""
    if not is_admin(update.message.from_user.id):
        await update.message.delete()  # Удаляем команду неадмина
        return
    
    # Получаем число после команды
    text = update.message.text.lower().strip()
    parts = text.split()
    
    if len(parts) < 2:
        await update.message.reply_text("❌ Укажи число: .варнлимит 5")
        return
    
    try:
        new_limit = int(parts[1])
        if new_limit < 1 or new_limit > 10:
            await update.message.reply_text("❌ Лимит должен быть от 1 до 10")
            return
        
        # Меняем лимит для всех пользователей
        for user_id in user_warns:
            user_warns[user_id]["limit"] = new_limit
        
        await update.message.reply_text(f"✅ Лимит варнов изменен на {new_limit} для всех!")
    except ValueError:
        await update.message.reply_text("❌ Укажи число!")

async def точка_варнлист(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .варнлист - список варнов (только для админов)"""
    if not is_admin(update.message.from_user.id):
        await update.message.delete()  # Удаляем команду неадмина
        return
    
    if not user_warns:
        await update.message.reply_text("📋 Список варнов пуст")
        return
    
    text = "📋 Список варнов:\n"
    for user_id, data in user_warns.items():
        try:
            user = await context.bot.get_chat(user_id)
            text += f"• {user.first_name}: {data['warns']}/{data['limit']}\n"
        except:
            text += f"• ID {user_id}: {data['warns']}/{data['limit']}\n"
    
    await update.message.reply_text(text)

async def старт_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /старт"""
    await update.message.reply_text(
        "✅ Бот работает!\n\n"
        "Доступные слова:\n"
        "• правила - ссылка на правила\n"
        "• сиси - поздороваться с Сиси\n"
        "• луми - про создателя\n"
        "• бот - проверить работу\n\n"
        "Команды с точкой (только для админов):\n"
        "• .дел - удалить сообщение\n"
        "• .пинг - проверить пинг\n"
        "• .варн - выдать варн\n"
        "• .варнлимит N - изменить лимит\n"
        "• .варнлист - список варнов"
    )

def main():
    """Запуск бота"""
    if not TOKEN:
        print("❌ Нет токена!")
        return
    
    print(f"📦 Загружено {len(RESPONSES)} команд")
    print(f"⚖️ Система варнов: {DEFAULT_WARN_LIMIT}/предупреждений")
    print(f"👑 Админы: {ADMIN_IDS}")
    
    app = Application.builder().token(TOKEN).build()
    
    # КОМАНДЫ С ТОЧКОЙ (только для админов)
    app.add_handler(MessageHandler(filters.Regex(r'^\.дел$') & filters.REPLY, точка_дел))
    app.add_handler(MessageHandler(filters.Regex(r'^\.пинг$'), точка_пинг))
    app.add_handler(MessageHandler(filters.Regex(r'^\.варн$') & filters.REPLY, точка_варн))
    app.add_handler(MessageHandler(filters.Regex(r'^\.варнлимит\s+\d+$'), точка_варнлимит))
    app.add_handler(MessageHandler(filters.Regex(r'^\.варнлист$'), точка_варнлист))
    
    # ОСТАЛЬНЫЕ КОМАНДЫ
    app.add_handler(CommandHandler("старт", старт_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🔥 БОТ ЗАПУЩЕН И РАБОТАЕТ!")
    print("Команды с точкой только для админов!")
    print("Ожидаю сообщения...")
    
    app.run_polling(drop_pending_updates=True)

# 🔥 ИСПРАВЛЕННАЯ СТРОКА - ДОЛЖНО БЫТЬ ДВОЙНОЕ ПОДЧЕРКИВАНИЕ
if __name__ == "__main__":
    main()
