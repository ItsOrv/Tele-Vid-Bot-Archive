#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Authentication handler for the bot."""

import logging
from telethon import events, Button
from database import database
from config import config

logger = logging.getLogger(__name__)

# States for the conversation handler
STATE_WAITING_PASSWORD = 1

# Store user states in memory (user_id -> state)
user_states = {}

async def register_auth_handlers(client):
    """Register all authentication handlers."""
    
    @client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        """Handle the /start command."""
        user_id = event.sender_id
        username = event.sender.username
        
        # Check if user is admin
        if user_id == config.ADMIN_ID:
            # Grant permanent access to admin
            database.save_user_access(user_id, username, expires_in=100 * 365 * 24 * 3600)  # ~100 years
            await show_main_menu(client, event)
            return
            
        # Check if user already has temporary access
        if database.check_user_access(user_id):
            await show_main_menu(client, event)
            return
            
        # Request password from non-admin users
        await event.respond(
            "Welcome to the Video Archive Bot!\n\n"
            "Please enter the access password to continue."
        )
        user_states[user_id] = STATE_WAITING_PASSWORD


    @client.on(events.NewMessage())
    async def message_handler(event):
        """Handle text messages for password verification."""
        user_id = event.sender_id
        
        # Ignore if the message is a command or from admin
        if event.message.text.startswith('/') or user_id == config.ADMIN_ID:
            return
            
        # Check if waiting for password
        if user_id in user_states and user_states[user_id] == STATE_WAITING_PASSWORD:
            # Verify password
            if event.text == config.ACCESS_PASSWORD:
                # Grant temporary access
                username = event.sender.username
                database.save_user_access(user_id, username)
                
                # Clear the state
                del user_states[user_id]
                
                await event.respond(
                    "✅ Password correct! You now have access for 1 hour."
                )
                await show_main_menu(client, event)
            else:
                await event.respond(
                    "❌ Incorrect password. Please try again or contact the administrator."
                )


async def check_access(event):
    """
    Check if user has access to the bot.
    
    Returns:
        bool: True if user has access, False otherwise
    """
    user_id = event.sender_id
    
    # Admin always has access
    if user_id == config.ADMIN_ID:
        return True
        
    # Check temporary access
    return database.check_user_access(user_id)


async def show_main_menu(client, event):
    """Display the main menu with inline buttons."""
    buttons = [
        [Button.inline("📁 Categories", data="menu_categories")],
        [Button.inline("🎬 Manage Videos", data="menu_manage_videos")],
        [Button.inline("🗂 Manage Categories", data="menu_manage_categories")]
    ]
    
    await event.respond(
        "📋 **Main Menu**\n\n"
        "Please select an option:",
        buttons=buttons
    ) 