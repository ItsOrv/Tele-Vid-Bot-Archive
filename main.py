#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient
from config import config
from database.database import init_db
from handlers import register_handlers

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot."""
    logger.info("Starting Telegram Video Archive Bot...")
    
    # Create DATA directories if they don't exist
    os.makedirs(config.VIDEO_DIR, exist_ok=True)
    os.makedirs(config.THUMBNAIL_DIR, exist_ok=True)
    
    # Initialize database
    init_db()
    
    # Create client
    client = TelegramClient('tele_vid_bot', config.API_ID, config.API_HASH)
    
    # Register all handlers
    await register_handlers(client)
    
    # Start the client
    await client.start(bot_token=config.BOT_TOKEN)
    logger.info("Bot started successfully!")
    
    # Run the client until disconnected
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the main function
    import asyncio
    asyncio.run(main()) 