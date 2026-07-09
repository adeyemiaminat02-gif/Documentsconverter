from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

def get_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("📂 Convert Document", callback_data="nav_convert")],
        [InlineKeyboardButton("📋 Supported Formats", callback_data="nav_formats")],
        [InlineKeyboardButton("❓ Help", callback_data="nav_help"), InlineKeyboardButton("ℹ️ About", callback_data="nav_about")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_conversion_targets_keyboard(targets: List[str], unique_id: str) -> InlineKeyboardMarkup:
    keyboard = []
    row = []
    for i, target in enumerate(targets):
        row.append(InlineKeyboardButton(target, callback_data=f"tgt|{target}|{unique_id}"))
        if len(row) == 3 or i == len(targets) - 1:
            keyboard.append(row)
            row = []
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel_conv")])
    return InlineKeyboardMarkup(keyboard)

def get_post_conversion_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔄 Convert Another Document", callback_data="nav_convert")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_settings_keyboard(current_settings: dict) -> InlineKeyboardMarkup:
    df = current_settings.get("default_output_format", "PDF")
    ko = current_settings.get("keep_original", "Yes")
    zb = current_settings.get("zip_batch", "Yes")
    
    keyboard = [
        [InlineKeyboardButton(f"Default Target: {df}", callback_data="set_toggle_df")],
        [InlineKeyboardButton(f"Keep Filename: {ko}", callback_data="set_toggle_ko")],
        [InlineKeyboardButton(f"ZIP Batches: {zb}", callback_data="set_toggle_zb")],
        [InlineKeyboardButton("🏁 Done", callback_data="set_done")]
    ]
    return InlineKeyboardMarkup(keyboard)
