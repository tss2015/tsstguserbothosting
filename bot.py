import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import settings
from database import db
from handlers.start import start
from handlers.authentication import lognum, logsession, auth_text
from handlers.account import status, logout, logout_callback
from handlers.tagall import tagall, cancel, tag_callback
from handlers.help import help_command
from handlers.admin import admin, stats, users, tasks, broadcast, maintenance

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

async def post_init(app):
    await db.connect()

async def post_shutdown(app):
    await db.close()

def build_application():
    app = Application.builder().token(settings.bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lognum", lognum))
    app.add_handler(CommandHandler("logsession", logsession))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("tagall", tagall))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("logout", logout))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(CommandHandler("tasks", tasks))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("maintenance", maintenance))

    app.add_handler(CallbackQueryHandler(tag_callback, pattern=r"^tag:(start|cancel)$"))
    app.add_handler(CallbackQueryHandler(logout_callback, pattern=r"^logout:(yes|no)$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auth_text))

    app.post_init = post_init
    app.post_shutdown = post_shutdown
    return app

if __name__ == "__main__":
    application = build_application()
    logger.info("Starting Telegram Userbot Manager")
    application.run_polling(allowed_updates=None)
