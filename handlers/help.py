from telegram import Update
from telegram.ext import ContextTypes

TEXT = """📚 *Commands*

/start — Open the control panel
/help — Show this help
/Lognum — Login using phone number
/Logsession — Login using an existing session
/status — Show account status
/tagall — Queue a safe member mention operation
/cancel — Cancel your active task
/Logout — Disconnect your account

Admin:
/admin /stats /users /tasks /broadcast /maintenance

⚠️ Telegram flood/rate limits are always respected. The bot does not bypass them.
"""

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT, parse_mode="Markdown")
