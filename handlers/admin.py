from telegram import Update
from telegram.ext import ContextTypes
from database import db
from config import settings

def is_admin(update):
    return update.effective_user and update.effective_user.id in settings.admin_ids

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return
    await update.message.reply_text(
        "🛡️ Admin panel\n/stats /users /tasks /broadcast /maintenance"
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    users = await db.users.count_documents({})
    running = await db.tasks.count_documents({"status": "SENDING"})
    completed = await db.tasks.count_documents({"status": "SENT"})
    failed = await db.tasks.count_documents({"status": "FAILED"})
    await update.message.reply_text(
        f"📊 Users: {users}\nRunning tasks: {running}\n"
        f"Completed: {completed}\nFailed: {failed}"
    )

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    count = await db.users.count_documents({})
    await update.message.reply_text(f"👥 Registered bot users: {count}")

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    count = await db.tasks.count_documents({})
    await update.message.reply_text(f"📋 Recorded tasks: {count}")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    await update.message.reply_text("Broadcast is intentionally left disabled by default. Implement an explicit recipient-consent policy before enabling it.")

async def maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update): return
    await update.message.reply_text("Maintenance controls are available for extension.")
