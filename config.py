"""
Configuration management for the Telegram Bot.

This module loads environment variables, defines constants, and 
validates the runtime configuration to ensure the bot can start safely.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Central configuration class.
    
    Attributes:
        TELEGRAM_BOT_TOKEN (str): The Telegram Bot API token.
        KAGGLE_USERNAME (str): Kaggle username for API authentication.
        KAGGLE_KEY (str): Kaggle API key.
        HF_TOKEN (str): HuggingFace API token.
        GITHUB_TOKEN (str): GitHub Personal Access Token.
        BASE_DIR (str): The absolute path to the project root.
        TEMP_DIR (str): The directory for temporary files (and zips).
    """
    
    # ---------------------------
    # Bot Configuration
    # ---------------------------
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # ---------------------------
    # API Credentials
    # ---------------------------
    KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY = os.getenv("KAGGLE_KEY")
    HF_TOKEN = os.getenv("HF_TOKEN")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    
    # ---------------------------
    # Directory Paths
    # ---------------------------
    BASE_DIR = os.getcwd()
    TEMP_DIR = os.path.join(BASE_DIR, "temp")
    
    @classmethod
    def validate(cls):
        """
        Validates critical configuration variables and initializes directories.

        Raises:
            ValueError: If required environment variables are missing.
        """
        missing = []
        if not cls.TELEGRAM_BOT_TOKEN:
            missing.append("TELEGRAM_BOT_TOKEN")
            
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        # Ensure critical directories exist
        try:
            os.makedirs(cls.TEMP_DIR, exist_ok=True)
        except OSError as e:
            raise ValueError(f"Failed to create TEMP_DIR at {cls.TEMP_DIR}: {e}")

# Run validation on import to fail fast during startup
try:
    Config.validate()
except Exception as e:
    # Print is used here because logger might not be initialized yet
    print(f"CRITICAL CONFIGURATION ERROR: {e}")
