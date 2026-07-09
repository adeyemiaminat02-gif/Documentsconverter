from telegram import Update
from telegram.ext import ContextTypes
from keyboards.inline import get_start_keyboard
from services.database import add_user

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return
    add_user(user.id, user.username, user.first_name)
    
    msg = (
        "📄 *Welcome to Documents Converting Bot!*\n\n"
        "I can quickly convert your documents into different file formats while preserving formatting whenever possible.\n\n"
        "*Supported formats include:*\n"
        "• PDF, DOCX, TXT, HTML\n"
        "• Markdown (MD), EPUB, RTF\n"
        "• ODT, CSV, XLSX, PPTX\n\n"
        "Select an action below or upload a file directly to get started!"
    )
    if update.message:
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_start_keyboard())
    elif update.callback_query:
        await update.callback_query.message.edit_text(msg, parse_mode="Markdown", reply_markup=get_start_keyboard())
