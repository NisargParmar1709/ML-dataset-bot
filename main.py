"""
Application Entry Point.

This script initializes the Telegram Bot, verifies configuration,
sets up necessary services, and starts the polling loop.
"""

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config
from utils.logger import setup_logger
from services.kaggle_service import KaggleService
from services.huggingface_service import HuggingFaceService
from services.github_service import GitHubService
from handlers.simple_handler import handle_message

# Setup Logger
logger = setup_logger()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the /start command.
    """
    await update.message.reply_text(
        "🤖 **Production Bot Ready**\n\n"
        "1. Send `MLparset` to get a ZIP of the temp folder.\n"
        "2. Send ANY text to search datasets (Links Only)."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Global Error Handler. Logs errors without crashing.
    """
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    # Optional: Notify user of internal error (be careful not to spam)

def main():
    """
    Main execution function.
    """
    # 1. Validate Configuration
    try:
        Config.validate()
        logger.info("Configuration validated.")
    except ValueError as e:
        logger.critical(f"Config Error: {e}")
        return

    # 2. Initialize Services
    # We initialize them here to inject them into bot_data
    services = {
        "kaggle": KaggleService(),
        "hf": HuggingFaceService(),
        "github": GitHubService()
    }
    
    # 3. Initialize Bot
    try:
        # Set explicit timeouts for production stability
        app = (
            ApplicationBuilder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            .connect_timeout(60.0)
            .read_timeout(1000.0)
            .write_timeout(1000.0)
            .build()
        )
        
        # Store services for handlers to access
        app.bot_data["services"] = services
        
        # Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Error Handler
        app.add_error_handler(error_handler)
        
        logger.info("✅ Bot started in POP (Production Optimized) mode.")
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.critical(f"Fatal error during bot startup: {e}", exc_info=True)

if __name__ == "__main__":
    main()
