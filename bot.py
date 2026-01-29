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

# ⚠️ СОЗДАТЕЛЬ - ТВОЙ ID ⚠️
CREATOR_ID = 7416252489  # Твой ID

# Хранилище рангов: {user_id: "rank"}
user_ranks = {
    CREATOR_ID: "creator"  # Создатель
}

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

def get_rank(user_id):
    """Получает ранг пользователя"""
    return user_ranks.get(user_id, "user")

def has_permission(user_id, required_rank):
    """Проверяет, имеет ли пользователь достаточный ранг"""
    rank_hierarchy = {
        "user": 0,
        "moderator": 1,
        "admin": 2,
        "head_admin": 3,
        "creator": 4
    }
    
    user_rank = get_rank(user_id)
    return rank_hierarchy.get(user_rank, 0) >= rank_hierarchy.get(required_rank, 0)

def is_creator(user_id):
    """Проверяет, является ли пользователь создателем"""
    return user_id == CREATOR_ID

def is_head_admin_or_higher(user_id):
    """Проверяет, является ли пользователь главным админом или выше"""
    return has_permission(user_id, "head_admin")

def is_admin_or_higher(user_id):
    """Проверяет, является ли пользователь админом или выше"""
    return has_permission(user_id, "admin")

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

async def get_user_from_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает пользователя из сообщения (ответ или упоминание)"""
    # 1. Если это ответ на сообщение
    if update.message.reply_to_message:
        return update.message.reply_to_message.from_user
    
    # 2. Если есть упоминание @username
    if update.message.entities:
        for entity in update.message.entities:
            if entity.type == "mention":
                username = update.message.text[entity.offset+1:entity.offset + entity.length]
                try:
                    # Пробуем найти пользователя по username в чате
                    members_count = await context.bot.get_chat_member_count(update.message.chat_id)
                    
                    # Ищем среди участников чата (упрощенный поиск)
                    # В реальности нужно кешировать участников или использовать базу данных
                    chat_members = []
                    for i in range(0, min(members_count, 100), 100):
                        try:
                            members = await context.bot.get_chat_administrators(update.message.chat_id)
                            chat_members.extend(members)
                        except:
                            break
                    
                    for member in chat_members:
                        if member.user.username and member.user.username.lower() == username.lower():
                            return member.user
                except Exception as e:
                    print(f"Ошибка поиска пользователя @{username}: {e}")
    
    return None

# ============ КОМАНДЫ МОДЕРАЦИИ ============

async def точка_дел(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .дел - удалить сообщение"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
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
    """Команда .пинг - проверка пинга"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    start_time = time.time()
    sent_message = await update.message.reply_text("🏓 Измеряю пинг...")
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 2)
    await sent_message.edit_text(f"🏓 Пинг бота: {ping_ms}мс")

async def точка_варн(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .варн - выдать предупреждение"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    target_user = await get_user_from_message(update, context)
    
    if not target_user:
        await update.message.reply_text("❌ Ответьте на сообщение или укажите @username")
        return
    
    user_id = target_user.id
    issuer_id = update.message.from_user.id
    
    # Нельзя выдавать варны создателю
    if is_creator(user_id):
        await update.message.reply_text("❌ Нельзя выдавать варны создателю!")
        return
    
    # Нельзя выдавать варны равным или высшим по рангу
    if has_permission(user_id, get_rank(issuer_id)):
        await update.message.reply_text("❌ Нельзя выдавать варны пользователям равного или высшего ранга!")
        return
    
    # Инициализируем если нет
    if user_id not in user_warns:
        user_warns[user_id] = {"warns": 0, "limit": DEFAULT_WARN_LIMIT}
    
    user_warns[user_id]["warns"] += 1
    warns = user_warns[user_id]["warns"]
    limit = user_warns[user_id]["limit"]
    
    await update.message.reply_text(
        f"⚠️ {target_user.first_name} получил предупреждение!\n"
        f"Варны: {warns}/{limit}"
    )
    
    # Если достиг лимита - МУТИМ
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
                f"🚫 {target_user.first_name} получил мут на 10 часов за {limit} предупреждений!"
            )
            # СБРАСЫВАЕМ ВАРНЫ ПОСЛЕ МУТА
            user_warns[user_id]["warns"] = 0
            print(f"♻️ Сбросил варны для {target_user.first_name} после мута")
        except Exception as e:
            await update.message.reply_text(f"❌ Не смог замутить: {e}")

async def точка_минус_варн(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда -варн - снять предупреждение"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    target_user = await get_user_from_message(update, context)
    
    if not target_user:
        await update.message.reply_text("❌ Ответьте на сообщение или укажите @username")
        return
    
    user_id = target_user.id
    issuer_id = update.message.from_user.id
    
    # Проверяем есть ли варны
    if user_id not in user_warns or user_warns[user_id]["warns"] <= 0:
        await update.message.reply_text(f"❌ У {target_user.first_name} нет варнов!")
        return
    
    # Нельзя снимать варны, которые выдавал ранг выше
    # Для простоты: проверяем может ли текущий пользователь выдавать варны этому пользователю
    if has_permission(user_id, get_rank(issuer_id)):
        await update.message.reply_text("❌ Нельзя снимать варны у пользователей равного или высшего ранга!")
        return
    
    user_warns[user_id]["warns"] -= 1
    warns = user_warns[user_id]["warns"]
    limit = user_warns[user_id]["limit"]
    
    await update.message.reply_text(
        f"✅ С {target_user.first_name} снято предупреждение!\n"
        f"Варны: {warns}/{limit}"
    )

# ============ КОМАНДЫ УПРАВЛЕНИЯ РАНГАМИ ============

async def точка_плюс_сс(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда +сс - назначить модератором"""
    if not is_head_admin_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    target_user = await get_user_from_message(update, context)
    
    if not target_user:
        await update.message.reply_text("❌ Ответьте на сообщение или укажите @username")
        return
    
    user_id = target_user.id
    
    # Нельзя назначать ранги создателю
    if is_creator(user_id):
        await update.message.reply_text("❌ Нельзя изменять ранг создателя!")
        return
    
    # Нельзя назначать выше своего ранга
    if has_permission(user_id, get_rank(update.message.from_user.id)):
        await update.message.reply_text("❌ Нельзя назначать ранг пользователю с равным или высшим рангом!")
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
    
    target_user = await get_user_from_message(update, context)
    
    if not target_user:
        await update.message.reply_text("❌ Ответьте на сообщение или укажите @username")
        return
    
    user_id = target_user.id
    
    # Назначаем главным админом
    user_ranks[user_id] = "head_admin"
    await update.message.reply_text(f"✅ {target_user.first_name} назначен Главным Администратором!")
    print(f"👑 Назначен главный админ: {target_user.first_name} (ID: {user_id})")

async def точка_минус_сс(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда -сс - снять ранг (понизить до пользователя)"""
    if not is_head_admin_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    target_user = await get_user_from_message(update, context)
    
    if not target_user:
        await update.message.reply_text("❌ Ответьте на сообщение или укажите @username")
        return
    
    user_id = target_user.id
    
    # Нельзя снимать ранги создателю
    if is_creator(user_id):
        await update.message.reply_text("❌ Нельзя изменять ранг создателя!")
        return
    
    # Нельзя снимать ранги пользователям с равным или высшим рангом
    if has_permission(user_id, get_rank(update.message.from_user.id)):
        await update.message.reply_text("❌ Нельзя снимать ранг пользователю с равным или высшим рангом!")
        return
    
    # Снимаем ранг (удаляем из словаря)
    if user_id in user_ranks:
        old_rank = user_ranks[user_id]
        del user_ranks[user_id]
        await update.message.reply_text(f"✅ С {target_user.first_name} снят ранг ({old_rank})!")
        print(f"🗑️ Снят ранг у: {target_user.first_name} (ID: {user_id}), был: {old_rank}")
    else:
        await update.message.reply_text(f"⚠️ {target_user.first_name} не имеет ранга!")

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
    rank_order = {"creator": 0, "head_admin": 1, "admin": 2, "moderator": 3}
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
            elif rank == "admin":
                rank_name = "👤 Администратор"  
            elif rank == "moderator":
                rank_name = "⚡ Модератор"
            else:
                rank_name = rank
            
            text += f"{rank_name}: {user.first_name} {username}\n"
        except:
            text += f"{rank}: ID {user_id}\n"
    
    await update.message.reply_text(text)

# ============ ДРУГИЕ КОМАНДЫ ============

async def точка_варнлимит(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда .варнлимит - изменить лимит варнов"""
    if not is_admin_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
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
    """Команда .варнлист - список варнов"""
    if not is_moderator_or_higher(update.message.from_user.id):
        await update.message.delete()
        return
    
    if not user_warns:
        await update.message.reply_text("📋 Список варнов пуст")
        return
    
    text = "📋 Список варнов:\n\n"
    for user_id, data in user_warns.items():
        try:
            user = await context.bot.get_chat(user_id)
            username = f"@{user.username}" if user.username else "нет @"
            text += f"• {user.first_name} {username}: {data['warns']}/{data['limit']}\n"
        except:
            text += f"• ID {user_id}: {data['warns']}/{data['limit']}\n"
    
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
    print(f"⚖️ Система варнов: {DEFAULT_WARN_LIMIT}/предупреждений")
    print(f"👑 Создатель: {CREATOR_ID}")
    
    app = Application.builder().token(TOKEN).build()
    
    # КОМАНДЫ МОДЕРАЦИИ (для модераторов и выше)
    app.add_handler(MessageHandler(filters.Regex(r'^\.дел$') & filters.REPLY, точка_дел))
    app.add_handler(MessageHandler(filters.Regex(r'^\.пинг$'), точка_пинг))
    app.add_handler(MessageHandler(filters.Regex(r'^\.варн.*'), точка_варн))
    app.add_handler(MessageHandler(filters.Regex(r'^\-варн.*'), точка_минус_варн))
    app.add_handler(MessageHandler(filters.Regex(r'^\.варнлимит\s+\d+$'), точка_варнлимит))
    app.add_handler(MessageHandler(filters.Regex(r'^\.варнлист$'), точка_варнлист))
    
    # КОМАНДЫ УПРАВЛЕНИЯ РАНГАМИ
    app.add_handler(MessageHandler(filters.Regex(r'^\+сс.*'), точка_плюс_сс))
    app.add_handler(MessageHandler(filters.Regex(r'^\+глсс.*'), точка_плюс_глсс))
    app.add_handler(MessageHandler(filters.Regex(r'^\-сс.*'), точка_минус_сс))
    app.add_handler(MessageHandler(filters.Regex(r'^\.садм$'), точка_садм))
    app.add_handler(MessageHandler(filters.Regex(r'^\.салл$'), точка_салл))
    
    # АНГЛИЙСКИЕ КОМАНДЫ
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🔥 БОТ ЗАПУЩЕН И РАБОТАЕТ!")
    print("🧭 Иерархия рангов: Создатель → Главный Админ → Админ → Модератор")
    print("Ожидаю сообщения...")
    
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
