import telebot
from telebot import types
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

admins = set()
banned = set()
muted = set()
warns = {}
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))  # замените на свой ID или через переменные

def is_admin(user_id):
    return user_id in admins or user_id == OWNER_ID

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "Привет! Я модерационный бот.")

@bot.message_handler(commands=['add_admin'])
def add_admin(msg):
    if msg.from_user.id != OWNER_ID:
        return bot.reply_to(msg, "Только владелец может назначать админов.")
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Ответьте на сообщение пользователя.")
    user_id = msg.reply_to_message.from_user.id
    admins.add(user_id)
    bot.reply_to(msg, f"@{msg.reply_to_message.from_user.username} теперь админ.")

@bot.message_handler(commands=['remove_admin'])
def remove_admin(msg):
    if msg.from_user.id != OWNER_ID:
        return bot.reply_to(msg, "Только владелец может снимать админов.")
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Ответьте на сообщение пользователя.")
    user_id = msg.reply_to_message.from_user.id
    admins.discard(user_id)
    bot.reply_to(msg, f"@{msg.reply_to_message.from_user.username} больше не админ.")

@bot.message_handler(commands=['ban'])
def ban(msg):
    if not is_admin(msg.from_user.id):
        return bot.reply_to(msg, "Нет прав.")
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Ответьте на сообщение пользователя.")
    user_id = msg.reply_to_message.from_user.id
    banned.add(user_id)
    try:
        bot.kick_chat_member(msg.chat.id, user_id)
    except Exception:
        pass
    bot.reply_to(msg, f"Пользователь @{msg.reply_to_message.from_user.username} забанен.")

@bot.message_handler(commands=['mute'])
def mute(msg):
    if not is_admin(msg.from_user.id):
        return bot.reply_to(msg, "Нет прав.")
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Ответьте на сообщение пользователя.")
    user_id = msg.reply_to_message.from_user.id
    muted.add(user_id)
    try:
        bot.restrict_chat_member(msg.chat.id, user_id, permissions=types.ChatPermissions(can_send_messages=False))
    except Exception:
        pass
    bot.reply_to(msg, f"Пользователь @{msg.reply_to_message.from_user.username} замьючен.")

@bot.message_handler(commands=['warn'])
def warn(msg):
    if not is_admin(msg.from_user.id):
        return bot.reply_to(msg, "Нет прав.")
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Ответьте на сообщение пользователя.")
    user_id = msg.reply_to_message.from_user.id
    warns[user_id] = warns.get(user_id, 0) + 1
    bot.reply_to(msg, f"@{msg.reply_to_message.from_user.username} получил предупреждение ({warns[user_id]}).")

@bot.message_handler(func=lambda m: True)
def check_user(msg):
    if msg.from_user.id in banned:
        bot.delete_message(msg.chat.id, msg.message_id)
    elif msg.from_user.id in muted:
        bot.delete_message(msg.chat.id, msg.message_id)

# словарь: user_id -> prefix
prefixes = {}
OWNER_ID = int(os.getenv("OWNER_ID", "123456789"))

def is_admin(user_id):
    return user_id == OWNER_ID  # для простоты: только владелец

@bot.message_handler(commands=['setprefix'])
def setprefix(msg):
    """Команда: /setprefix <префикс> (ответом на сообщение пользователя)"""
    if not is_admin(msg.from_user.id):
        return bot.reply_to(msg, "Нет прав.")
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Ответьте на сообщение пользователя.")
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2:
        return bot.reply_to(msg, "Использование: /setprefix <префикс>")
    prefix = parts[1].strip()
    user_id = msg.reply_to_message.from_user.id
    prefixes[user_id] = prefix
    username = msg.reply_to_message.from_user.username or msg.reply_to_message.from_user.first_name
    bot.reply_to(msg, f"Для @{username} установлен префикс: {prefix}")

@bot.message_handler(commands=['prefixes'])
def show_prefixes(msg):
    """Вывести список всех пользователей с префиксами"""
    if not prefixes:
        return bot.reply_to(msg, "Префиксов пока нет.")
    lines = []
    for user_id, prefix in prefixes.items():
        lines.append(f"{user_id} — {prefix}")
    text = "Список префиксов:\n" + "\n".join(lines)
    bot.reply_to(msg, text)

@bot.message_handler(commands=['clearprefix'])
def clearprefix(msg):
    """Снять префикс"""
    if not is_admin(msg.from_user.id):
        return bot.reply_to(msg, "Нет прав.")
    if not msg.reply_to_message:
        return bot.reply_to(msg, "Ответьте на сообщение пользователя.")
    user_id = msg.reply_to_message.from_user.id
    if user_id in prefixes:
        prefixes.pop(user_id)
        bot.reply_to(msg, "Префикс снят.")
    else:
        bot.reply_to(msg, "У этого пользователя нет префикса.")

if __name__ == "__main__":
    bot.infinity_polling()
