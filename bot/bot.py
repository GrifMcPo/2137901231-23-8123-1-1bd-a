import asyncio
import json
import os
import yaml
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import subprocess

# Конфигурация
BOT_TOKEN = "8886183344:AAE6p7g9SH1d0qalxcgrQu-_TvbkkkVVLjA"
ADMINS_FILE = os.path.join(os.path.dirname(__file__), 'admins.yml')
BANS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'bans.json')

# Загрузка админов
def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('admins', {})
    return {}

# Загрузка банов
def load_bans():
    if os.path.exists(BANS_FILE):
        with open(BANS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_bans(bans):
    with open(BANS_FILE, 'w', encoding='utf-8') as f:
        json.dump(bans, f, indent=2, ensure_ascii=False)

# Получение кастомного имени админа
def get_admin_name(telegram_id):
    admins = load_admins()
    admin_data = admins.get(str(telegram_id))
    if admin_data:
        return admin_data.get('custom_name', f'Admin_{telegram_id}')
    return f'User_{telegram_id}'

# Обработка команды !rcon
async def rcon_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    
    user_id = str(update.effective_user.id)
    admins = load_admins()
    
    # Проверка прав админа
    if user_id not in admins:
        await update.message.reply_text("❌ У вас нет прав для использования этой команды.")
        return
    
    # Парсим команду
    text = update.message.text
    parts = text.split(maxsplit=2)
    
    if len(parts) < 3:
        await update.message.reply_text("Использование: !rcon site <команда>")
        return
    
    command = parts[2]
    admin_name = get_admin_name(user_id)
    
    # Выполняем команду RCON (здесь вы можете добавить свою логику)
    try:
        # Пример выполнения RCON команды
        # result = subprocess.run(['rcon', command], capture_output=True, text=True)
        
        # Имитация выполнения
        result = f"Команда '{command}' выполнена от имени {admin_name}"
        
        # Логируем в баны, если это бан
        if 'ban' in command.lower():
            bans = load_bans()
            ban_data = {
                'banned_by': admin_name,
                'telegram_id': user_id,
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'admin_custom_name': admin_name
            }
            bans[f"ban_{len(bans) + 1}"] = ban_data
            save_bans(bans)
        
        await update.message.reply_text(f"✅ {result}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

# Старт бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    admins = load_admins()
    
    if user_id in admins:
        admin_name = get_admin_name(user_id)
        await update.message.reply_text(
            f"👋 Привет, {admin_name}!\n"
            "Используй команду:\n"
            "!rcon site <команда>"
        )
    else:
        await update.message.reply_text("👋 Привет! У вас нет доступа к этому боту.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text("!rcon") & filters.COMMAND, rcon_command))
    application.add_handler(MessageHandler(filters.Regex(r'^!rcon'), rcon_command))
    
    print("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
