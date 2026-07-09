from telegram import Update
from telegram.ext import ContextTypes
from services.database import get_settings, update_setting
from keyboards.inline import get_settings_keyboard

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    current_settings = get_settings(user_id)
    
    msg = "⚙️ *User Layout Configuration Panel*\nAdjust core parameters for automated runs:"
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=get_settings_keyboard(current_settings))

async def settings_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data
    
    current_settings = get_settings(user_id)
    
    if data == "set_toggle_df":
        formats = ["PDF", "DOCX", "TXT", "HTML", "MD"]
        idx = (formats.index(current_settings["default_output_format"]) + 1) % len(formats) if current_settings["default_output_format"] in formats else 0
        update_setting(user_id, "default_output_format", formats[idx])
    elif data == "set_toggle_ko":
        new_val = "No" if current_settings["keep_original"] == "Yes" else "Yes"
        update_setting(user_id, "keep_original", new_val)
    elif data == "set_toggle_zb":
        new_val = "No" if current_settings["zip_batch"] == "Yes" else "Yes"
        update_setting(user_id, "zip_batch", new_val)
    elif data == "set_done":
        await query.message.edit_text("✅ *Settings finalized and saved safely.*", parse_mode="Markdown")
        return

    updated_settings = get_settings(user_id)
    await query.message.edit_reply_markup(reply_markup=get_settings_keyboard(updated_settings))
