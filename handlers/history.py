from telegram import Update
from telegram.ext import ContextTypes
from services.database import get_history

async def history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    history_records = get_history(user_id, limit=10)
    
    if not history_records:
        await update.message.reply_text("📋 *No conversion tracking records found in your structural profile history.*", parse_mode="Markdown")
        return
        
    msg = "📋 *Your Recent 10 Document Conversions:*\n\n"
    for i, record in enumerate(history_records, 1):
        msg += (
            f"*{i}. {record['original_filename']}*\n"
            f"├ Transition: `{record['source_format']}` ➡️ `{record['target_format']}`\n"
            f"└ Timestamp: `{record['timestamp']}`\n\n"
        )
    await update.message.reply_text(msg, parse_mode="Markdown")
