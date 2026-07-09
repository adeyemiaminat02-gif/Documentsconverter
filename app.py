import sys
import os
import threading
import asyncio
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from utils.config import BOT_TOKEN
from utils.logger import logger
from services.database import init_db
from handlers.start import start_handler
from handlers.help import help_handler
from handlers.about import about_handler
from handlers.history import history_handler
from handlers.settings import settings_handler, settings_callback_handler
from handlers.convert import document_upload_handler, conversion_action_callback, text_routing_fallback_handler

# Dummy server to satisfy Render's Web Service Port requirement
def run_dummy_server():
    port = int(os.getenv("PORT", 10000))
    server_address = ("", port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    logger.info(f"Dummy health check server listening on port {port}")
    httpd.serve_forever()

async def async_main() -> None:
    if not BOT_TOKEN:
        logger.critical("CRITICAL: BOT_TOKEN environment target missing in configuration context.")
        sys.exit(1)
        
    logger.info("Initializing persistence database layers...")
    init_db()
    
    # Start the dummy web server in a background thread if running on Render
    if os.getenv("PORT"):
        threading.Thread(target=run_dummy_server, daemon=True).start()
    
    logger.info("Configuring python-telegram-bot asynchronous application stack frame context...")
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Command Dispatcher Registration
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("about", about_handler))
    app.add_handler(CommandHandler("history", history_handler))
    app.add_handler(CommandHandler("settings", settings_handler))
    
    # Dynamic Navigation Callback Query Wireframes
    app.add_handler(CallbackQueryHandler(start_handler, pattern="^nav_start$"))
    app.add_handler(CallbackQueryHandler(about_handler, pattern="^nav_about$"))
    app.add_handler(CallbackQueryHandler(help_handler, pattern="^nav_help|^nav_formats$"))
    
    # Config / Setting State Callbacks
    app.add_handler(CallbackQueryHandler(settings_callback_handler, pattern="^set_"))
    
    # File Stream Converters & Data Event Interceptors
    app.add_handler(MessageHandler(filters.Document.ALL, document_upload_handler))
    app.add_handler(CallbackQueryHandler(conversion_action_callback, pattern="^(tgt|cancel_conv)"))
    
    # Fallback Handling Mechanics
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_routing_fallback_handler))
    
    logger.info("Bot infrastructure initialization complete. Launching execution event loops polling updates...")
    
    # Explicitly initialize, start, and run polling within our active managed loop
    await app.initialize()
    await app.updater.start_polling()
    await app.start()
    
    # Keeps the loop alive until terminated
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping bot execution container cleanly...")
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

def main() -> None:
    # Python 3.14 robust main entry point loop isolation
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
