"""
Core request handlers for the Telegram Bot.

This module implements the two Main Modes of the bot:
1. Mode 1 (MLparset): Zips and sends contents of the temp folder.
2. Mode 2 (Search): Performs dataset searches across multiple platforms.
"""

import os
import logging
import zipfile
import tempfile
import shutil
from telegram import Update
from telegram.ext import ContextTypes
from config import Config

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Router for incoming text messages.
    
    Args:
        update (Update): The Telegram update object.
        context (ContextTypes.DEFAULT_TYPE): The callback context.
    """
    text = update.message.text.strip() if update.message.text else ""
    
    # --- MODE 1: MLparset (Secure File Dump) ---
    if text == "MLparset":
        logger.info(f"User {update.effective_user.id} requested MLparset dump.")
        await _handle_mlparset(update, context)
        return

    # --- MODE 2: Dataset Search (Link Only) ---
    await _handle_search(update, context, text)

async def _handle_mlparset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Mode 1: Zips and sends all files from the temp directory.
    Uses a temporary file for the zip to avoid concurrency issues with fixed path names.
    """
    temp_dir = Config.TEMP_DIR
    
    # 1. Validation
    if not os.path.exists(temp_dir):
        await update.message.reply_text("❌ Temp directory is missing.")
        return

    files_to_zip = [
        f for f in os.listdir(temp_dir) 
        if os.path.isfile(os.path.join(temp_dir, f)) and not f.endswith('.zip')
    ]
    
    if not files_to_zip:
        await update.message.reply_text("📂 Temp folder is empty. No files to send.")
        return

    status_msg = await update.message.reply_text("📦 Compressing content...")
    
    # 2. ZIP Creation (Defensive)
    # Use a Safe Temporary File for the ZIP
    try:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
            zip_path = tmp_zip.name
        
        logger.info(f"Creating zip at {zip_path} with {len(files_to_zip)} files.")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filename in files_to_zip:
                file_path = os.path.join(temp_dir, filename)
                try:
                    zf.write(file_path, arcname=filename)
                except OSError as e:
                    logger.warning(f"Skipping locked file {filename}: {e}")
        
        # 3. Sending
        await status_msg.edit_text("📤 Uploading bundle...")
        
        with open(zip_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                caption=f"📦 **MLparset Dump**\n✅ Files: {len(files_to_zip)}",
                filename="ml_datasets_bundle.zip"
            )
            
        logger.info("Zip file sent successfully.")

    except Exception as e:
        logger.error(f"Failed to create/send zip: {e}", exc_info=True)
        await status_msg.edit_text("❌ Error processing request. Please try again.")
        
    finally:
        # 4. Cleanup
        # We only remove the TEMPORARY ZIP, not the source files (Mode 1 requirements didn't say to delete source)
        if 'zip_path' in locals() and os.path.exists(zip_path):
            try:
                os.remove(zip_path)
                logger.info(f"Cleaned up temporary zip: {zip_path}")
            except OSError as e:
                logger.error(f"Failed to delete temp zip: {e}")

async def _handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
    """
    Mode 2: Searches Kaggle, HuggingFace, and GitHub. Returns LINKS ONLY.
    """
    if not query:
        return

    await update.message.reply_text(f"🔍 Searching for '{query}'...")
    
    services = context.bot_data.get("services", {})
    results = []

    # Aggregated Search with Error Isolation
    # 1. Kaggle
    if services.get("kaggle"):
        results.extend(services["kaggle"].search_datasets(query))

    # 2. HuggingFace
    if services.get("hf"):
        results.extend(services["hf"].search_datasets(query))

    # 3. GitHub
    if services.get("github"):
        results.extend(services["github"].search_repositories(query))

    if not results:
        await update.message.reply_text("❌ No results found. Try a broader keyword.")
        return

    # Format Output: LINKS ONLY
    response = f"🔎 **Results for '{query}'**\n\n"
    
    # Take top 10 mixed results
    for i, res in enumerate(results[:10]):
        # Defensive check for keys
        platform = res.get('platform', 'Unknown')
        title = res.get('title', 'Untitled')
        url = res.get('url', '#')
        
        platform_icon = "🏆" if platform == 'Kaggle' else "🤗" if platform == 'HuggingFace' else "💻"
        
        # Markdown escaping could be added here if needed, but simple brackets usually safe enough for titles
        response += f"{i+1}. {platform_icon} [{title}]({url})\n"

    try:
        await update.message.reply_markdown(response, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Failed to send markdown response: {e}")
        # Fallback to plain text if Markdown parsing fails
        await update.message.reply_text("⚠️ formatting error, but here are the results:\n" + response.replace('*', ''))
