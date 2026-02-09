"""
Custom logging configuration for the Telegram Bot.

This module provides a centralized production-grade logger setup
that output to the console (stdout) with structured formatting.
"""

import logging
import sys

def setup_logger(name: str = "Bot") -> logging.Logger:
    """
    Configures and returns a production-ready console logger.

    Args:
        name (str): The name of the logger (default: "Bot").

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent adding duplicate handlers if setup is called multiple times
    if logger.hasHandlers():
        return logger
    
    # Use stdout for container/systemd compatibility
    handler = logging.StreamHandler(sys.stdout)
    
    # Format: [Time] [Level] [Module] Message
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
