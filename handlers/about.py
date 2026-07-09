from telegram import Update
from telegram.ext import ContextTypes

async def about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    about_text = (
        "ℹ️ *About @DocumentsConvertingBot*\n\n"
        "• *Version*: `1.0.0-Prod` \n"
        "• *Environment*: Python 3.12 (Async Engine Architecture)\n"
        "• *Engine Foundations*: Pandoc, PyMuPDF, PdfPlumber, Weasyprint Core Engine\n"
        "• *Developer System Profile*: [Production Environment Placeholder]\n\n"
        "Designed for reliable, fast document layout structural transitions."
    )
    if update.message:
        await update.message.reply_text(about_text, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(about_text, parse_mode="Markdown")
