#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Category handler for managing categories."""

import logging
from telethon import events, Button
from database import database
from utils.media_utils import delete_video_files
from handlers.auth_handler import check_access, show_main_menu

logger = logging.getLogger(__name__)

# States for conversation
STATE_WAITING_CATEGORY_NAME = 1
STATE_CONFIRM_DELETE = 2

# Store user states (user_id -> (state, context))
user_states = {}


async def register_category_handlers(client):
    """Register all category-related handlers."""
    
    @client.on(events.CallbackQuery(pattern=r"menu_manage_categories"))
    async def on_manage_categories(event):
        """Handle the category management menu button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        buttons = [
            [Button.inline("➕ Add Category", data="category_add")],
            [Button.inline("➖ Delete Category", data="category_delete")],
            [Button.inline("🔙 Back to Main Menu", data="back_to_main")]
        ]
        
        await event.edit(
            "🗂 **Manage Categories**\n\n"
            "Please select an action:",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"category_add"))
    async def on_category_add(event):
        """Handle the add category button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        user_id = event.sender_id
        user_states[user_id] = (STATE_WAITING_CATEGORY_NAME, {})
        
        await event.edit(
            "➕ **Add Category**\n\n"
            "Please send me the name of the new category, or click Cancel.",
            buttons=[Button.inline("Cancel", data="back_to_categories")]
        )


    @client.on(events.CallbackQuery(pattern=r"category_delete"))
    async def on_category_delete(event):
        """Handle the delete category button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Fetch all categories
        categories = database.get_all_categories()
        
        if not categories:
            await event.edit(
                "❌ **No categories found**\n\n"
                "There are no categories to delete.",
                buttons=[Button.inline("🔙 Back", data="menu_manage_categories")]
            )
            return
        
        # Create buttons for each category
        buttons = [
            [Button.inline(f"{cat['name']}", data=f"delete_cat_{cat['id']}")] 
            for cat in categories
        ]
        buttons.append([Button.inline("Cancel", data="back_to_categories")])
        
        await event.edit(
            "➖ **Delete Category**\n\n"
            "Select a category to delete:",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"delete_cat_(\d+)"))
    async def on_delete_category_selected(event):
        """Handle selection of a category for deletion."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Extract category ID from callback data
        category_id = int(event.data.decode().split('_')[2])
        
        # Get category name for confirmation
        categories = database.get_all_categories()
        category_name = next((cat['name'] for cat in categories if cat['id'] == category_id), "Unknown")
        
        # Store category ID for later deletion
        user_id = event.sender_id
        user_states[user_id] = (STATE_CONFIRM_DELETE, {'category_id': category_id})
        
        # Ask for confirmation
        buttons = [
            [Button.inline("✅ Yes, delete", data=f"confirm_delete_{category_id}")],
            [Button.inline("No, cancel", data="category_delete")]
        ]
        
        await event.edit(
            f"⚠️ **Confirm Deletion**\n\n"
            f"Are you sure you want to delete the category **{category_name}**?\n\n"
            f"⚠️ **WARNING:** This will also delete all videos in this category!",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"confirm_delete_(\d+)"))
    async def on_confirm_delete(event):
        """Handle confirmation of category deletion."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Extract category ID from callback data
        category_id = int(event.data.decode().split('_')[2])
        
        # Delete the category and get associated videos
        videos = database.delete_category(category_id)
        
        # Delete video files
        for video in videos:
            delete_video_files(video)
        
        await event.edit(
            "✅ **Category Deleted**\n\n"
            f"The category and all its videos have been successfully deleted.",
            buttons=[Button.inline("🔙 Back", data="menu_manage_categories")]
        )


    @client.on(events.CallbackQuery(pattern=r"back_to_categories"))
    async def on_back_to_categories(event):
        """Handle back to categories button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Clear user state
        user_id = event.sender_id
        if user_id in user_states:
            del user_states[user_id]
        
        # Show manage categories menu
        buttons = [
            [Button.inline("➕ Add Category", data="category_add")],
            [Button.inline("➖ Delete Category", data="category_delete")],
            [Button.inline("🔙 Back to Main Menu", data="back_to_main")]
        ]
        
        await event.edit(
            "🗂 **Manage Categories**\n\n"
            "Please select an action:",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"back_to_main"))
    async def on_back_to_main(event):
        """Handle back to main menu button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Clear user state
        user_id = event.sender_id
        if user_id in user_states:
            del user_states[user_id]
        
        # Show main menu
        await show_main_menu(client, event)


    @client.on(events.NewMessage())
    async def on_message(event):
        """Handle messages for category operations."""
        user_id = event.sender_id
        
        # Check if user is in a state
        if user_id not in user_states:
            return
        
        state, context = user_states[user_id]
        
        # Handle waiting for category name
        if state == STATE_WAITING_CATEGORY_NAME:
            category_name = event.text.strip()
            
            # Validate category name
            if not category_name:
                await event.respond(
                    "❌ **Invalid Name**\n\n"
                    "Category name cannot be empty. Please try again.",
                    buttons=[Button.inline("Cancel", data="back_to_categories")]
                )
                return
            
            # Add the category
            category_id = database.add_category(category_name)
            
            if category_id:
                # Clear state
                del user_states[user_id]
                
                # Send success message
                await event.respond(
                    "✅ **Category Added**\n\n"
                    f"The category '{category_name}' has been successfully added!",
                    buttons=[Button.inline("🔙 Back", data="menu_manage_categories")]
                )
            else:
                await event.respond(
                    "❌ **Error**\n\n"
                    "Failed to add category. It might already exist.",
                    buttons=[Button.inline("🔙 Back", data="menu_manage_categories")]
                )


async def show_categories_menu(client, event):
    """Show the categories menu for video browsing."""
    # Fetch all categories
    categories = database.get_all_categories()
    
    if not categories:
        await event.edit(
            "❌ **No Categories**\n\n"
            "There are no categories available yet.",
            buttons=[Button.inline("🔙 Back to Main Menu", data="back_to_main")]
        )
        return
    
    # Create buttons for each category
    buttons = [
        [Button.inline(f"{cat['name']}", data=f"browse_cat_{cat['id']}")] 
        for cat in categories
    ]
    buttons.append([Button.inline("🔙 Back to Main Menu", data="back_to_main")])
    
    await event.edit(
        "📁 **Categories**\n\n"
        "Select a category to view videos:",
        buttons=buttons
    ) 