"""
Application Entry Point (Production/Render Ready).

This script initializes the Telegram Bot, verifies configuration,
sets up necessary services, starts a background health-check HTTP server
(to satisfy Render's port binding requirement), and runs the bot polling loop.
"""

import logging
import os
import threading
import http.server
import socketserver
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, Defaults
from config import Config
from utils.logger import setup_logger
from services.kaggle_service import KaggleService
from services.huggingface_service import HuggingFaceService
from services.github_service import GitHubService
from handlers.simple_handler import handle_message

# Setup Logger
logger = setup_logger()

# ---------------------------------------------------------
# 1. Minimal HTTP Health Server (For Render Port Binding)
# ---------------------------------------------------------
class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    """
    Minimal Request Handler that returns 200 OK.
    Use this to trick Render into thinking we are a web service.
    """
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running.")

    def log_message(self, format, *args):
        # Silence HTTP logs to keep console clean
        pass

def start_health_server():
    """
    Starts a background HTTP server on the port defined by existing environment variables.
    Render sets the 'PORT' variable automatically.
    """
    port = int(os.environ.get("PORT", 10000))
    try:
        # Allow reuse address to prevent 'Address already in use' on restarts
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("0.0.0.0", port), HealthCheckHandler) as httpd:
            logger.info(f"🌍 Health check server listening on port {port}")
            httpd.serve_forever()
    except Exception as e:
        logger.critical(f"Failed to start health server: {e}")

# ---------------------------------------------------------
# 2. Bot Logic
# ---------------------------------------------------------

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

    # 2. Start Health Server (Background Thread)
    # This must run continuously to keep the container alive on Render
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()

    # 3. Initialize Services
    services = {
        "kaggle": KaggleService(),
        "hf": HuggingFaceService(),
        "github": GitHubService()
    }
    
    # 4. Initialize Bot with Network Hardening
    try:
        # Hardened Network Settings for Unstable Free Tier
        app = (
            ApplicationBuilder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            # Connection Hardening
            .connect_timeout(60.0)      # Wait longer for initial connection
            .read_timeout(60.0)         # Wait longer for data (Render latency)
            .write_timeout(60.0)        # Wait longer to send data
            .get_updates_read_timeout(60.0) # Specific for polling loop
            .pool_timeout(60.0)         # Wait longer for pool slot
            .connection_pool_size(1024) # Allow many concurrent connections
            .build()
        )
        
        # Store services
        app.bot_data["services"] = services
        
        # Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Error Handler
        app.add_error_handler(error_handler)
        
        logger.info("✅ Bot started in Render-Ready mode.")
        
        # Run Polling with Robustness
        app.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.critical(f"Fatal error during bot startup: {e}", exc_info=True)

if __name__ == "__main__":
    main()
