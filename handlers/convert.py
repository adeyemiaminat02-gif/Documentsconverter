import os
import uuid
from telegram import Update
from telegram.ext import ContextTypes
from utils.config import MAX_FILE_SIZE_MB, OUTPUT_DIR
from utils.logger import logger
from services.converter import get_valid_targets, convert_file
from services.file_manager import save_file, create_zip_archive, clean_files
from services.database import add_history, get_settings
from keyboards.inline import get_conversion_targets_keyboard, get_post_conversion_keyboard

# In-memory tracking cache for active concurrent multi-batch queues
USER_BATCH_CACHE = {}

async def document_upload_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    user_id = update.effective_user.id
    
    doc = message.document
    if not doc:
        return

    # Check safe binary size parameters
    if doc.file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
        await message.reply_text(f"❌ *File too large.* Limit is {MAX_FILE_SIZE_MB}MB.", parse_mode="Markdown")
        return

    orig_filename = doc.file_name or "Unknown.txt"
    ext = os.path.splitext(orig_filename)[1].upper().replace('.', '')
    
    valid_targets = get_valid_targets(ext)
    if not valid_targets:
        await message.reply_text(f"❌ Format type `.{ext}` conversion matrix handling is missing or invalid.", parse_mode="Markdown")
        return

    # Download payload binary chunk
    processing_msg = await message.reply_text("⏳ *Downloading transaction file payload data...*", parse_mode="Markdown")
    tg_file = await context.bot.get_file(doc.file_id)
    file_bytes = await tg_file.download_as_bytearray()
    
    unique_id = str(uuid.uuid4())[:8]
    local_path = save_file(unique_id, file_bytes, orig_filename)
    
    # Track items for single uploads and multi-file batches
    if user_id not in USER_BATCH_CACHE:
        USER_BATCH_CACHE[user_id] = []
        
    USER_BATCH_CACHE[user_id].append({
        'id': unique_id,
        'local_path': local_path,
        'filename': orig_filename,
        'ext': ext,
        'valid_targets': valid_targets
    })

    await processing_msg.delete()
    
    # Prompt confirmation layout
    prompt_msg = (
        f"📦 *Uploaded Successfully*\n\n"
        f"📄 *File Name*: `{orig_filename}`\n"
        f"🔍 *Detected Format*: `{ext}`\n\n"
        f"Select the target system transformation matrix:"
    )
    await message.reply_text(prompt_msg, parse_mode="Markdown", reply_markup=get_conversion_targets_keyboard(valid_targets, unique_id))

async def conversion_action_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    data_parts = query.data.split('|')
    
    if data_parts[0] == "cancel_conv":
        if user_id in USER_BATCH_CACHE:
            for item in USER_BATCH_CACHE[user_id]:
                clean_files([item['local_path']])
            del USER_BATCH_CACHE[user_id]
        await query.message.edit_text("❌ *Conversion request sequence dropped by user.*", parse_mode="Markdown")
        return

    if len(data_parts) != 3 or data_parts[0] != "tgt":
        return

    target_format = data_parts[1]
    target_item_id = data_parts[2]
    
    if user_id not in USER_BATCH_CACHE or not USER_BATCH_CACHE[user_id]:
        await query.message.edit_text("❌ *Session timed out or pipeline container empty.*", parse_mode="Markdown")
        return

    await query.message.edit_text(f"⚙️ *Compiling conversion process to {target_format}...*", parse_mode="Markdown")
    
    user_items = USER_BATCH_CACHE[user_id]
    user_settings = get_settings(user_id)
    
    converted_files_paths = []
    source_files_to_clean = []
    
    try:
        # If user batch holds multiple documents, process them sequentially
        if len(user_items) > 1 and user_settings.get("zip_batch") == "Yes":
            for item in user_items:
                source_files_to_clean.append(item['local_path'])
                # Check cross-compatibility dynamically
                if target_format in get_valid_targets(item['ext']):
                    out = convert_file(item['local_path'], target_format, OUTPUT_DIR)
                    converted_files_paths.append(out)
                    add_history(user_id, item['filename'], item['ext'], target_format)
            
            archive_name = f"Batch_Conversions_{uuid.uuid4().hex[:6]}.zip"
            zip_out = create_zip_archive(converted_files_paths, archive_name)
            
            await query.message.reply_document(
                document=open(zip_out, 'rb'),
                filename=archive_name,
                caption="✅ *Batch Conversion Completed Successfully (Compressed ZIP)*",
                parse_mode="Markdown",
                reply_markup=get_post_conversion_keyboard()
            )
            clean_files([zip_out] + converted_files_paths)
            
        else:
            # Handle single document pipelines
            active_item = next((i for i in user_items if i['id'] == target_item_id), user_items[0])
            source_files_to_clean.append(active_item['local_path'])
            
            out_file = convert_file(active_item['local_path'], target_format, OUTPUT_DIR)
            add_history(user_id, active_item['filename'], active_item['ext'], target_format)
            
            final_name = active_item['filename'] if user_settings.get("keep_original") == "Yes" else os.path.basename(out_file)
            if not final_name.endswith(f".{target_format.lower()}"):
                final_name = f"{os.path.splitext(final_name)[0]}.{target_format.lower()}"
                
            await query.message.reply_document(
                document=open(out_file, 'rb'),
                filename=final_name,
                caption="✅ *Conversion Completed Successfully*",
                parse_mode="Markdown",
                reply_markup=get_post_conversion_keyboard()
            )
            clean_files([out_file])
            
    except Exception as err:
        logger.error(f"Execution Error in conversion runtime thread loop: {str(err)}", exc_info=True)
        await query.message.reply_text(
            f"❌ *An unhandled error occurred during conversion.*\n"
            f"Ensure the document is not password-protected or corrupted.\n"
            f"Error details: `{str(err)}`",
            parse_mode="Markdown"
        )
    finally:
        clean_files(source_files_to_clean)
        if user_id in USER_BATCH_CACHE:
            del USER_BATCH_CACHE[user_id]
        try:
            await query.message.delete()
        except Exception:
            pass

async def text_routing_fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    if "Convert Document" in text or "nav_convert" in text:
        await update.message.reply_text("📥 *Please send or drag/drop document file(s) directly to this conversation window.*", parse_mode="Markdown")
