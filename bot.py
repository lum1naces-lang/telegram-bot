import os
import time
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

TOKEN = os.getenv("TOKEN")

print("=" * 50)
print("🤖 Бот запускается...")
time.sleep(3)
print("✅ Начинаю работу")

# ⚠️ СОЗДАТЕЛЬ - ТВОЙ ID ⚠️
CREATOR_ID = 7416252489  # Твой ID

# Хранилище рангов: {user_id: "rank"}
# Ранги: "creator", "head_admin", "moderator"
user_ranks = {
    CREATOR_ID: "creator"  # Создатель
}

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

def get_rank(user_id):
    """Получает ранг пользователя"""
    return user_ranks.get(user_id, "user")

def has_permission(user_id, required_rank):
    """Проверяет, имеет ли пользователь достаточный ранг"""
    rank_hierarchy = {
        "user": 0,
        "moderator": 1,
        "head_admin": 2,
        "creator": 3
    }
    
    user_rank = get_rank(user_id)
    return rank_hierarchy.get(user_rank, 0) >= rank_hierarchy.get(required_rank, 0)

def is_creator(user_id):
    """Проверяет, является ли пользователь создателем"""
    return get_rank(user_id) == "creator"

def is_head_admin_or_higher(user_id):
    """Проверяет, является ли пользователь главным админом или выше"""
    return has_permission(user_id, "head_admin")

def is_moderator_or_higher(user_id):
    """Проверяет, является ли пользователь модератором или выше"""
    return has_permission(user_id, "moderator")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений"""
    text = update.message.text.lower().strip()
    
    for keyword, response in RESPONSES.items():
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

async def get_target_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает целевого пользователя из сообщения"""
    # 1. Если это ответ на сообщение
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    
    # 2. Если есть упоминание @username
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "mention":
                mention = update.message.text[entity.offset:entity.offset + entity.length]
                username = mention[1:]  # Убираем @
                
                try:
                    # Пробуем получить пользователя по username
                    # В Telegram API нет прямого метода по username, 
                    # но можем попробовать через get_chat если username известен
                    # Упрощенная реализация - вернем None и обработаем в командах
                    return {"type": "mention", "username": username}
                except:
                    pass
    
    # 3. Если указан ID (цифры после команды)
    text = update.message.text.strip()
    parts = text.split()
    if len(parts) > 1:
        try:
            user_id = int(parts[1])
            try:
                user = await context.bot.get_chat(user_id)
                return user
            except:
                return {"type": "id", "user_id": user_id}
        except ValueError:
            pass
    
    return None

async def resolve_user_from_data(user_data, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Преобразует данные о пользователе в объект пользователя"""
    if isinstance(user_data, dict):
        if user_data.get("type") == "mention":
            username = user_data.get("username")
            # Пытаемся найти пользователя в чате
            try:
                # Получаем всех участников чата
                async for member in context.bot.get_chat_members(update.message.chat_id):
                    if member.user.username and member.user.username.lower() == username.lower():
                        return member.user
            except:
                pass
            return None
        elif user_data.get("type") == "id":
            user_id = user_data.get("user_id")
            try:
                return await context.bot.get_chat(user_id)
            except:
                return None
    return user_data  # Уже объект пользователя

async def точка_дел(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .дел - удалить сообщение"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Ответьте на сообщение!")
        await update.message.delete()
        return
    
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
    """Команда .пинг - проверка пинга"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    start_time = time.time()
    sent_message = await update.message.reply_text("🏓 Измеряю пинг...")
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 2)
    await sent_message.edit_text(f"🏓 Пинг бота: {ping_ms}мс")

# ============ КОМАНДЫ УПРАВЛЕНИЯ РАНГАМИ ============

async def точка_плюс_сс(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда +сс - назначить модератором"""
    if not is_head_admin_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    user_data = await get_target_user(update, context)
    if not user_data:
        await update.message.reply_text("❌ Укажите пользователя (ответьте на сообщение, @username или ID)!")
        await update.message.delete()
        return
    
    target_user = await resolve_user_from_data(user_data, update, context)
    if not target_user:
        await update.message.reply_text("❌ Не удалось найти пользователя!")
        await update.message.delete()
        return
    
    user_id = target_user.id
    
    # Нельзя назначать ранги создателю
    if is_creator(user_id):
        await update.message.reply_text("❌ Нельзя изменять ранг создателя!")
        await update.message.delete()
        return
    
    # Нельзя назначать выше своего ранга
    if has_permission(user_id, get_rank(update.message.from_user.id)):
        await update.message.reply_text("❌ Нельзя назначать ранг пользователю с равным или высшим рангом!")
        await update.message.delete()
        return
    
    # Назначаем модератором
    user_ranks[user_id] = "moderator"
    await update.message.reply_text(f"✅ {target_user.first_name} назначен Модератором!")
    print(f"👤 Назначен модератор: {target_user.first_name} (ID: {user_id})")

async def точка_плюс_глсс(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда +глсс - назначить главным админом"""
    if not is_creator(update.message.from_user.id):
        await update.message.delete()
        return
    
    user_data = await get_target_user(update, context)
    if not user_data:
        await update.message.reply_text("❌ Укажите пользователя (ответьте на сообщение, @username или ID)!")
        await update.message.delete()
        return
    
    target_user = await resolve_user_from_data(user_data, update, context)
    if not target_user:
        await update.message.reply_text("❌ Не удалось найти пользователя!")
        await update.message.delete()
        return
    
    user_id = target_user.id
    
    # Нельзя назначать создателя
    if is_creator(user_id):
        await update.message.reply_text("❌ Это создатель!")
        await update.message.delete()
        return
    
    # Назначаем главным админом
    user_ranks[user_id] = "head_admin"
    await update.message.reply_text(f"✅ {target_user.first_name} назначен Главным Администратором!")
    print(f"👑 Назначен главный админ: {target_user.first_name} (ID: {user_id})")

async def точка_минус_сс(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда -сс - снять ранг"""
    if not is_head_admin_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    user_data = await get_target_user(update, context)
    if not user_data:
        await update.message.reply_text("❌ Укажите пользователя (ответьте на сообщение, @username или ID)!")
        await update.message.delete()
        return
    
    target_user = await resolve_user_from_data(user_data, update, context)
    if not target_user:
        await update.message.reply_text("❌ Не удалось найти пользователя!")
        await update.message.delete()
        return
    
    user_id = target_user.id
    
    # Нельзя снимать ранги создателю
    if is_creator(user_id):
        await update.message.reply_text("❌ Нельзя изменять ранг создателя!")
        await update.message.delete()
        return
    
    # Нельзя снимать ранги пользователям с равным или высшим рангом
    if has_permission(user_id, get_rank(update.message.from_user.id)):
        await update.message.reply_text("❌ Нельзя снимать ранг пользователю с равным или высшим рангом!")
        await update.message.delete()
        return
    
    # Снимаем ранг (удаляем из словаря)
    if user_id in user_ranks:
        old_rank = user_ranks[user_id]
        del user_ranks[user_id]
        await update.message.reply_text(f"✅ С {target_user.first_name} снят ранг ({old_rank})!")
        print(f"🗑️ Снят ранг у: {target_user.first_name} (ID: {user_id}), был: {old_rank}")
    else:
        await update.message.reply_text(f"⚠️ {target_user.first_name} не имеет ранга!")
        await update.message.delete()

async def точка_кик(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда +кик - исключить пользователя"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    user_data = await get_target_user(update, context)
    if not user_data:
        await update.message.reply_text("❌ Укажите пользователя (ответьте на сообщение, @username или ID)!")
        await update.message.delete()
        return
    
    target_user = await resolve_user_from_data(user_data, update, context)
    if not target_user:
        await update.message.reply_text("❌ Не удалось найти пользователя!")
        await update.message.delete()
        return
    
    user_id = target_user.id
    
    # Нельзя кикать пользователей с равным или высшим рангом
    if has_permission(user_id, get_rank(update.message.from_user.id)):
        await update.message.reply_text("❌ Нельзя исключить пользователя с равным или высшим рангом!")
        await update.message.delete()
        return
    
    try:
        await context.bot.ban_chat_member(
            chat_id=update.message.chat_id,
            user_id=user_id
        )
        await context.bot.unban_chat_member(
            chat_id=update.message.chat_id,
            user_id=user_id
        )
        await update.message.reply_text(f"🚫 {target_user.first_name} был исключен!")
        print(f"👢 Исключен: {target_user.first_name} (ID: {user_id})")
    except Exception as e:
        await update.message.reply_text(f"❌ Не смог исключить: {e}")

async def точка_салл(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .салл - снять ВСЕ ранги (кроме создателя)"""
    if not is_creator(update.message.from_user.id):
        await update.message.delete()
        return
    
    # Сохраняем создателя
    saved_creator = {CREATOR_ID: "creator"}
    
    # Считаем сколько было админов/модераторов
    removed_count = len(user_ranks) - 1  # Минус создатель
    
    # Оставляем только создателя
    user_ranks.clear()
    user_ranks.update(saved_creator)
    
    await update.message.reply_text(f"✅ Сняты все ранги! Удалено: {removed_count} пользователей")
    print(f"🔥 Сняты все ранги, остался только создатель")

async def точка_садм(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .садм - список всех рангов"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    if len(user_ranks) <= 1:  # Только создатель
        await update.message.reply_text("👑 Есть только Создатель!")
        return
    
    # Сортируем по рангам
    rank_order = {"creator": 0, "head_admin": 1, "moderator": 2}
    sorted_users = sorted(
        [(uid, rank) for uid, rank in user_ranks.items() if uid != CREATOR_ID],
        key=lambda x: rank_order.get(x[1], 99)
    )
    
    text = "👑 Список рангов:\n\n"
    
    # Сначала создатель
    try:
        creator_user = await context.bot.get_chat(CREATOR_ID)
        username = f"@{creator_user.username}" if creator_user.username else "нет @"
        text += f"👑 Создатель: {creator_user.first_name} {username}\n\n"
    except:
        text += f"👑 Создатель: ID {CREATOR_ID}\n\n"
    
    # Остальные ранги
    for user_id, rank in sorted_users:
        try:
            user = await context.bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else "нет @"
            
            if rank == "head_admin":
                rank_name = "👑 Администратор"
            elif rank == "moderator":
                rank_name = "⚡ Модератор"
            else:
                rank_name = rank
            
            text += f"{rank_name}: {user.first_name} {username}\n"
        except:
            text += f"{rank}: ID {user_id}\n"
    
    await update.message.reply_text(text)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text("Работаю")

def main():
    """Запуск бота"""
    if not TOKEN:
        print("❌ Нет токена!")
        return
    
    print(f"📦 Загружено {len(RESPONSES)} команд")
    print(f"👑 Создатель: {CREATOR_ID}")
    
    app = Application.builder().token(TOKEN).build()
    
    # БАЗОВЫЕ КОМАНДЫ (для модераторов и выше)
    app.add_handler(MessageHandler(filters.Regex(r'^\.дел$') & filters.REPLY, точка_дел))
    app.add_handler(MessageHandler(filters.Regex(r'^\.пинг$'), точка_пинг))
    
    # КОМАНДЫ УПРАВЛЕНИЯ РАНГАМИ И КИКА
    app.add_handler(MessageHandler(filters.Regex(r'^\+сс\b.*'), точка_плюс_сс))  # +сс или +сс @username
    app.add_handler(MessageHandler(filters.Regex(r'^\+глсс\b.*'), точка_плюс_глсс))  # +глсс или +глсс @username
    app.add_handler(MessageHandler(filters.Regex(r'^\-сс\b.*'), точка_минус_сс))  # -сс или -сс @username
    app.add_handler(MessageHandler(filters.Regex(r'^\+кик\b.*'), точка_кик))  # +кик или +кик @username
    
    # КОМАНДЫ УПРАВЛЕНИЯ
    app.add_handler(MessageHandler(filters.Regex(r'^\.садм$'), точка_садм))
    app.add_handler(MessageHandler(filters.Regex(r'^\.салл$'), точка_салл))
    
    # АНГЛИЙСКИЕ КОМАНДЫ
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🔥 БОТ ЗАПУЩЕН И РАБОТАЕТ!")
    print("🧭 Иерархия рангов: Создатель → Главный Админ → Модератор")
    print("🎮 Команды работают тремя способами:")
    print("   1. Ответ на сообщение: +сс")
    print("   2. По @username: +сс @username")
    print("   3. По ID: +сс 123456789")
    print("Ожидаю сообщения...")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
