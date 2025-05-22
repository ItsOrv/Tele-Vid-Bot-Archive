#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Configuration module for the bot."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for the bot."""
    
    # Telegram API credentials
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # Admin and access control
    ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
    ACCESS_PASSWORD = os.getenv("ACCESS_PASSWORD", "")
    
    # Access timeout in seconds (1 hour)
    ACCESS_TIMEOUT = 3600
    
    # Database
    DB_PATH = "database/video_archive.db"
    
    # Directories
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "DATA")
    VIDEO_DIR = os.path.join(DATA_DIR, "videos")
    THUMBNAIL_DIR = os.path.join(DATA_DIR, "thumbnails")

# Create a config instance
config = Config()

# Validate essential configuration
if not all([config.API_ID, config.API_HASH, config.BOT_TOKEN, config.ADMIN_ID, config.ACCESS_PASSWORD]):
    raise ValueError("Missing required environment variables. Please check your .env file.") 