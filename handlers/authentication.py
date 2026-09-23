from telegram import Update
from telegram.ext import ContextTypes
from database import db
from config import settings
from services.session_manager import SessionManager
from services.telegram_client import manager

session_manager = SessionManager(settings.session_encryption_key)

async def lognum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["auth_state"] = "phone"
    await update.message.reply_text(
        "🔐 Send your Telegram phone number in international format.\n"
        "Temporary login data is kept only in memory."
    )

async def logsession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["auth_state"] = "session"
    await update.message.reply_text(
        "🔑 Send your existing Telethon StringSession.\n"
        "Do not send it anywhere else. It will never be echoed back."
    )

async def auth_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("auth_state")
    if state == "session":
        session = update.message.text.strip()
        context.user_data.pop("auth_state", None)
        try:
            client = await manager.connect_session(
                update.effective_user.id, session, settings.api_id, settings.api_hash
            )
            me = await client.get_me()
            encrypted = session_manager.encrypt(session)
            await db.users.update_one(
                {"bot_user_id": update.effective_user.id},
                {"$set": {
                    "bot_user_id": update.effective_user.id,
                    "telegram_user_id": me.id,
                    "username": me.username,
                    "first_name": me.first_name,
                    "authenticated": True,
                    "encrypted_session": encrypted,
                }},
                upsert=True,
            )
            await update.message.delete()
            await update.effective_chat.send_message(
                "✅ Telegram account connected successfully."
            )
        except Exception:
            await update.message.reply_text(
                "❌ The session could not be authorized. Check the session and try again."
            )
        return

    if state == "phone":
        await update.message.reply_text(
            "For security, this starter implementation does not place Telegram OTP "
            "or 2FA credentials into persistent storage. Use /Logsession after creating "
            "an authorized StringSession through a trusted local environment."
        )
        context.user_data.pop("auth_state", None)
