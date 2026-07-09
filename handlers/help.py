from telegram import Update
from telegram.ext import ContextTypes
from utils.config import MAX_FILE_SIZE_MB

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "❓ *How to Use This Bot*\n\n"
        "1️⃣ **Upload Document(s)**: Send any supported single document or multiple items directly to the chat.\n"
        "2️⃣ **Choose Target Format**: Pick your target transformation format from the dynamic inline buttons.\n"
        "3️⃣ **Download**: The bot returns your single file, or aggregates files into a compressed ZIP archive.\n\n"
        f"📍 *Max Allowed File Size*: `{MAX_FILE_SIZE_MB}MB`\n\n"
        "ℹ️ *Available Telegram System Directives*:\n"
        "/start - Reset context & greet user\n"
        "/help - Show usage guidelines\n"
        "/history - Fetch last 10 conversions\n"
        "/settings - Adjust output parameters\n"
        "/about - Runtime engine specifications"
    )
    if update.message:
        await update.message.reply_text(help_text, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(help_text, parse_mode="Markdown")
