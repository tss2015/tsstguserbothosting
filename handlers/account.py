from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import db
from services.telegram_client import manager

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    record = await db.users.find_one({"bot_user_id": update.effective_user.id})
    if not record or not record.get("authenticated"):
        await update.message.reply_text("🔐 Account: Not connected")
        return
    await update.message.reply_text(
        "📊 *Account Status*\n"
        f"Connection: Connected\n"
        f"Name: {record.get('first_name', '-')}\n"
        f"Username: @{record.get('username') or '-'}\n"
        f"Telegram ID: {record.get('telegram_user_id', '-')}\n"
        f"Client: {'Running' if update.effective_user.id in manager.clients else 'Stopped'}",
        parse_mode="Markdown",
    )

async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("✅ Yes, Logout", callback_data="logout:yes"),
        InlineKeyboardButton("❌ Cancel", callback_data="logout:no"),
    ]]
    await update.message.reply_text(
        "⚠️ Are you sure you want to logout?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def logout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "logout:no":
        await query.edit_message_text("Logout cancelled.")
        return
    uid = query.from_user.id
    await manager.disconnect(uid)
    await db.users.delete_one({"bot_user_id": uid})
    await query.edit_message_text("🚪 Logged out successfully. Your stored session was removed.")
