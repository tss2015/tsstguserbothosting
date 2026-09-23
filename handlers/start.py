from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from database import db

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    record = await db.users.find_one({"bot_user_id": user.id})
    connected = bool(record and record.get("authenticated"))
    name = record.get("first_name", "-") if record else "-"
    username = record.get("username") if record else None
    status = "Connected" if connected else "Not connected"

    text = (
        "🤖 *Telegram Userbot Manager*\\n"
        "━━━━━━━━━━━━━━━━━━━━\\n"
        f"🔐 Account: *{status}*\\n"
        f"👤 User: @{username}" if username else f"👤 User: {name}"
    )
    text += (
        "\\n\\n━━━━━━━━━━━━━━━━━━━━\\n"
        "Available Features:\\n"
        "📢 Tag All Members\\n"
        "🔐 Login with Number\\n"
        "🔑 Login with Session\\n"
        "📊 Account Status\\n"
        "🛑 Cancel Tasks\\n"
        "🚪 Logout"
    )

    keyboard = [
        [InlineKeyboardButton("🔐 Login with Number", callback_data="login:number"),
         InlineKeyboardButton("🔑 Login with Session", callback_data="login:session")],
        [InlineKeyboardButton("📊 Account Status", callback_data="account:status")],
        [InlineKeyboardButton("🚪 Logout", callback_data="logout:yes")],
        [InlineKeyboardButton("❓ Help", callback_data="help")],
    ]
    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )
