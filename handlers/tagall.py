import asyncio
import uuid
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from telethon.errors import FloodWaitError
from database import db
from config import settings
from services.telegram_client import manager
from services.member_collector import eligible_members
from services.mention_manager import mention, batches
from services.rate_limiter import RateLimiter
from services.task_manager import UserTask, task_manager
from utils.helpers import utcnow, human_seconds

limiter = RateLimiter()

async def tagall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    client = manager.clients.get(uid)
    if not client:
        await update.message.reply_text("🔐 Connect your Telegram account first.")
        return
    if update.effective_chat.type not in ("group", "supergroup"):
        await update.message.reply_text("❌ /tagall can only be used in a group or supergroup.")
        return

    members = await eligible_members(client, update.effective_chat)
    if not members:
        await update.message.reply_text("No eligible members were found.")
        return

    estimated = len(members) * settings.tag_delay
    task_id = str(uuid.uuid4())
    await db.tasks.insert_one({
        "task_id": task_id, "bot_user_id": uid,
        "chat_id": update.effective_chat.id, "task_type": "tagall",
        "status": "QUEUED", "total_members": len(members),
        "processed_members": 0, "successful": 0, "failed": 0,
        "created_at": utcnow()
    })
    context.user_data["pending_tag"] = (task_id, update.effective_chat.id, members)

    keyboard = [[
        InlineKeyboardButton("▶️ Start", callback_data="tag:start"),
        InlineKeyboardButton("❌ Cancel", callback_data="tag:cancel")
    ]]
    await update.message.reply_text(
        f"📢 *Tag operation preview*\n\n"
        f"Group: {update.effective_chat.title or '-'}\n"
        f"Eligible members: {len(members)}\n"
        f"Delay: {settings.tag_delay:g}s\n"
        f"Estimated minimum duration: {human_seconds(estimated)}\n\n"
        "⚠️ Telegram rate limits may pause this operation.",
        reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if query.data == "tag:cancel":
        context.user_data.pop("pending_tag", None)
        await query.edit_message_text("❌ Tag operation cancelled.")
        return

    if task_manager.get(uid):
        await query.edit_message_text("⚠️ You already have a running task.")
        return

    pending = context.user_data.pop("pending_tag", None)
    if not pending:
        await query.edit_message_text("This operation has expired. Run /tagall again.")
        return

    task_id, chat_id, members = pending
    item = UserTask(task_id, uid, chat_id)
    task_manager.add(item)
    item.task = asyncio.create_task(run_tagging(query, item, members))

async def run_tagging(query, item, members):
    uid = item.bot_user_id
    client = manager.clients.get(uid)
    sent = failed = 0
    await db.tasks.update_one({"task_id": item.task_id}, {"$set": {"status": "SENDING"}})
    try:
        for batch in batches(members, 5):
            if item.cancel_event.is_set():
                await db.tasks.update_one({"task_id": item.task_id},
                    {"$set": {"status": "CANCELLED", "processed_members": sent + failed}})
                await query.edit_message_text("🛑 Tagging process cancelled.")
                return
            text = " ".join(mention(u) for u in batch)
            try:
                await limiter.wait(f"{uid}:{item.chat_id}", settings.tag_delay)
                await client.send_message(item.chat_id, text, link_preview=False)
                sent += len(batch)
            except FloodWaitError as exc:
                await db.tasks.update_one({"task_id": item.task_id},
                    {"$set": {"status": "FLOOD_WAIT", "flood_wait_seconds": exc.seconds}})
                await query.edit_message_text(
                    f"⏸️ Telegram requested a flood wait of {exc.seconds}s. "
                    "The task has been paused safely."
                )
                return
            except Exception:
                failed += len(batch)
            await db.tasks.update_one({"task_id": item.task_id},
                {"$set": {"processed_members": sent + failed,
                          "successful": sent, "failed": failed}})
        await db.tasks.update_one({"task_id": item.task_id},
            {"$set": {"status": "SENT", "completed_at": utcnow()}})
        await query.edit_message_text(
            f"✅ Tagging completed.\nSent: {sent}\nFailed: {failed}"
        )
    finally:
        task_manager.remove(uid)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if task_manager.cancel(update.effective_user.id):
        await update.message.reply_text("🛑 Cancellation requested.")
    else:
        await update.message.reply_text("No active tagging task.")
