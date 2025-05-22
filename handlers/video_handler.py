#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Video handler for managing videos."""

import os
import logging
import traceback
from telethon import events, Button
from telethon.tl.types import DocumentAttributeVideo, MessageMediaPhoto
from database import database
from utils.media_utils import save_video_file, is_valid_url, delete_video_files
from handlers.auth_handler import check_access
from handlers.category_handler import show_categories_menu

logger = logging.getLogger(__name__)

# States for conversation
STATE_WAITING_TITLE = 1
STATE_WAITING_VIDEO = 2
STATE_WAITING_CATEGORY = 3
STATE_CONFIRM_DELETE = 4

# Store user states (user_id -> (state, context))
user_states = {}


async def register_video_handlers(client):
    """Register all video-related handlers."""
    
    @client.on(events.CallbackQuery(pattern=r"menu_manage_videos"))
    async def on_manage_videos(event):
        """Handle the video management menu button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        buttons = [
            [Button.inline("➕ Add Video", data="video_add")],
            [Button.inline("➖ Delete Video", data="video_delete")],
            [Button.inline("🔙 Back to Main Menu", data="back_to_main")]
        ]
        
        await event.edit(
            "🎬 **Manage Videos**\n\n"
            "Please select an action:",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"video_add"))
    async def on_video_add(event):
        """Handle the add video button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        user_id = event.sender_id
        # Set state to waiting for title
        user_states[user_id] = (STATE_WAITING_TITLE, {})
        
        await event.edit(
            "➕ **Add Video**\n\n"
            "Please send me the title of the new video, or click Cancel.",
            buttons=[Button.inline("Cancel", data="back_to_videos")]
        )


    @client.on(events.CallbackQuery(pattern=r"video_delete"))
    async def on_video_delete(event):
        """Handle the delete video button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Fetch all categories
        categories = database.get_all_categories()
        
        if not categories:
            await event.edit(
                "❌ **No categories found**\n\n"
                "There are no categories with videos to delete.",
                buttons=[Button.inline("🔙 Back", data="menu_manage_videos")]
            )
            return
        
        # Create buttons for each category
        buttons = [
            [Button.inline(f"{cat['name']}", data=f"delete_video_cat_{cat['id']}")] 
            for cat in categories
        ]
        buttons.append([Button.inline("Cancel", data="back_to_videos")])
        
        await event.edit(
            "➖ **Delete Video**\n\n"
            "Select a category first:",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"delete_video_cat_(\d+)"))
    async def on_delete_video_category_selected(event):
        """Handle selection of a category for video deletion."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Extract category ID from callback data
        category_id = int(event.data.decode().split('_')[3])
        
        # Get all videos in this category
        videos = database.get_videos_by_category(category_id)
        
        if not videos:
            await event.edit(
                "❌ **No videos found**\n\n"
                "There are no videos in this category.",
                buttons=[Button.inline("🔙 Back", data="video_delete")]
            )
            return
        
        # Create buttons for each video
        buttons = [
            [Button.inline(f"{video['title']}", data=f"delete_video_{video['id']}")] 
            for video in videos
        ]
        buttons.append([Button.inline("Cancel", data="video_delete")])
        
        await event.edit(
            "➖ **Delete Video**\n\n"
            "Select a video to delete:",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"delete_video_(\d+)"))
    async def on_delete_video_selected(event):
        """Handle selection of a video for deletion."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Extract video ID from callback data
        video_id = int(event.data.decode().split('_')[2])
        
        # Get video details
        video = database.get_video(video_id)
        if not video:
            await event.edit(
                "❌ **Error**\n\n"
                "Video not found. It might have been deleted already.",
                buttons=[Button.inline("🔙 Back", data="video_delete")]
            )
            return
        
        # Store video ID for later deletion
        user_id = event.sender_id
        user_states[user_id] = (STATE_CONFIRM_DELETE, {'video_id': video_id})
        
        # Ask for confirmation
        buttons = [
            [Button.inline("✅ Yes, delete", data=f"confirm_delete_video_{video_id}")],
            [Button.inline("No, cancel", data="video_delete")]
        ]
        
        await event.edit(
            f"⚠️ **Confirm Deletion**\n\n"
            f"Are you sure you want to delete the video **{video['title']}**?",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"confirm_delete_video_(\d+)"))
    async def on_confirm_delete_video(event):
        """Handle confirmation of video deletion."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Extract video ID from callback data
        video_id = int(event.data.decode().split('_')[3])
        
        # Delete the video
        video = database.delete_video(video_id)
        
        if video:
            # Delete video file
            delete_video_files(video)
            
            await event.edit(
                "✅ **Video Deleted**\n\n"
                f"The video '{video['title']}' has been successfully deleted.",
                buttons=[Button.inline("🔙 Back", data="menu_manage_videos")]
            )
        else:
            await event.edit(
                "❌ **Error**\n\n"
                "Failed to delete video. It might have been deleted already.",
                buttons=[Button.inline("🔙 Back", data="menu_manage_videos")]
            )


    @client.on(events.CallbackQuery(pattern=r"back_to_videos"))
    async def on_back_to_videos(event):
        """Handle back to videos button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Clear user state
        user_id = event.sender_id
        if user_id in user_states:
            del user_states[user_id]
        
        # Show manage videos menu
        buttons = [
            [Button.inline("➕ Add Video", data="video_add")],
            [Button.inline("➖ Delete Video", data="video_delete")],
            [Button.inline("🔙 Back to Main Menu", data="back_to_main")]
        ]
        
        await event.edit(
            "🎬 **Manage Videos**\n\n"
            "Please select an action:",
            buttons=buttons
        )


    @client.on(events.CallbackQuery(pattern=r"select_category_(\d+)"))
    async def on_category_selected(event):
        """Handle category selection for adding a video."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        user_id = event.sender_id
        if user_id not in user_states:
            await event.edit(
                "❌ **Error**\n\n"
                "Session expired. Please start over.",
                buttons=[Button.inline("🔙 Back", data="video_add")]
            )
            return
        
        # Extract category ID from callback data
        category_id = int(event.data.decode().split('_')[2])
        
        # Update user context with selected category
        state, context = user_states[user_id]
        context['category_id'] = category_id
        user_states[user_id] = (state, context)
        
        # Get the video data from context
        title = context.get('title')
        video_type = context.get('type')
        path_or_url = context.get('path_or_url')
        thumbnail_path = context.get('thumbnail_path')
        
        # Add the video to the database
        video_id = database.add_video(title, video_type, path_or_url, category_id, thumbnail_path)
        
        if video_id:
            # Clear user state
            del user_states[user_id]
            
            # Show success message
            await event.edit(
                "✅ **Video Added**\n\n"
                f"The video '{title}' has been successfully added!",
                buttons=[Button.inline("🔙 Back", data="menu_manage_videos")]
            )
        else:
            await event.edit(
                "❌ **Error**\n\n"
                "Failed to add video to the database.",
                buttons=[Button.inline("🔙 Back", data="menu_manage_videos")]
            )


    @client.on(events.CallbackQuery(pattern=r"menu_categories"))
    async def on_categories_menu(event):
        """Handle the categories menu button."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        await show_categories_menu(client, event)


    @client.on(events.CallbackQuery(pattern=r"browse_cat_(\d+)"))
    async def on_browse_category(event):
        """Handle selection of a category for browsing."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Extract category ID from callback data
        category_id = int(event.data.decode().split('_')[2])
        
        # Get all categories for name lookup
        categories = database.get_all_categories()
        category_name = next((cat['name'] for cat in categories if cat['id'] == category_id), "Unknown")
        
        # Get all videos in this category
        videos = database.get_videos_by_category(category_id)
        
        if not videos:
            await event.edit(
                f"📁 **{category_name}**\n\n"
                "There are no videos in this category.",
                buttons=[Button.inline("🔙 Back", data="menu_categories")]
            )
            return
        
        # Tell user we're sending videos
        await event.edit(
            f"📁 **{category_name}**\n\n"
            "Sending videos in this category...",
            buttons=[Button.inline("🔙 Back", data="menu_categories")]
        )
        
        # Send each video
        for video in videos:
            # Create view button
            if video['type'] == 'file':
                caption = f"🎬 **{video['title']}**"
                buttons = [[Button.inline("▶️ View Video", data=f"play_video_{video['id']}")]]
                
                # Send thumbnail with caption and button
                if video['thumbnail_path'] and os.path.exists(video['thumbnail_path']):
                    await client.send_file(
                        event.chat_id,
                        file=video['thumbnail_path'],
                        caption=caption,
                        buttons=buttons
                    )
                else:
                    # No thumbnail, just send text
                    await client.send_message(
                        event.chat_id,
                        caption,
                        buttons=buttons
                    )
            else:
                # Link type video
                url = video['path_or_url']
                caption = f"🔗 **{video['title']}**\n\n{url}"
                await client.send_message(
                    event.chat_id,
                    caption,
                    buttons=[[Button.url("🔗 Open Link", url)]]
                )
        
        # Send completion message
        await client.send_message(
            event.chat_id,
            "✅ All videos in this category have been sent.",
            buttons=[[Button.inline("⬅️ Return to Main Menu", data="back_to_main")]]
        )


    @client.on(events.CallbackQuery(pattern=r"play_video_(\d+)"))
    async def on_play_video(event):
        """Handle playing a video file."""
        if not await check_access(event):
            await event.answer("Access expired. Please restart the bot with /start.")
            return
        
        # Extract video ID from callback data
        video_id = int(event.data.decode().split('_')[2])
        
        # Get video details
        video = database.get_video(video_id)
        if not video:
            await event.answer("Video not found. It might have been deleted.")
            return
        
        if video['type'] != 'file':
            await event.answer("This is a link, not a file.")
            return
        
        # Send the video file
        if os.path.exists(video['path_or_url']):
            await event.answer("Sending video...")
            caption = f"🎬 **{video['title']}**"
            await client.send_file(
                event.chat_id,
                file=video['path_or_url'],
                caption=caption,
                supports_streaming=True
            )
        else:
            await event.answer("Video file not found on the server.")


    @client.on(events.NewMessage())
    async def on_message(event):
        """Handle messages for video operations."""
        user_id = event.sender_id
        
        # Check if user is in a state
        if user_id not in user_states:
            return
        
        state, context = user_states[user_id]
        logger.info(f"Processing message from user {user_id} in state {state}")
        
        # Handle waiting for video title
        if state == STATE_WAITING_TITLE:
            title = event.text.strip()
            logger.info(f"Received title: '{title}'")
            
            if not title:
                logger.warning(f"User {user_id} provided empty title")
                await event.respond(
                    "❌ **Invalid Title**\n\n"
                    "Title cannot be empty. Please try again.",
                    buttons=[Button.inline("Cancel", data="back_to_videos")]
                )
                return
            
            # Save title and update state to waiting for video
            context['title'] = title
            user_states[user_id] = (STATE_WAITING_VIDEO, context)
            logger.info(f"Title saved, user {user_id} moved to STATE_WAITING_VIDEO")
            
            await event.respond(
                "🎬 **Video Upload**\n\n"
                f"Title: **{title}**\n\n"
                "Please send me one of the following:\n\n"
                "1️⃣ **Video File**: Upload a video file from your device\n\n"
                "2️⃣ **Video Link**: Send a link to a video from YouTube, Vimeo, or similar video platforms\n\n"
                "Note: Video files must have a valid format and links must be from supported video platforms.",
                buttons=[Button.inline("Cancel", data="back_to_videos")]
            )
            return
        
        # Handle waiting for video
        elif state == STATE_WAITING_VIDEO:
            logger.info(f"Processing video or link from user {user_id}")
            # Check if it's a link
            if event.text and not event.media:
                url = event.text.strip()
                logger.info(f"Received text as potential URL: {url}")
                
                if not is_valid_url(url):
                    logger.warning(f"Invalid URL received: {url}")
                    await event.respond(
                        "❌ **Invalid URL**\n\n"
                        "Please send a valid video URL from supported platforms like YouTube, Vimeo, etc.",
                        buttons=[Button.inline("Cancel", data="back_to_videos")]
                    )
                    return
                
                # Save link and move to category selection
                logger.info(f"Valid URL detected, saving: {url}")
                context['type'] = 'link'
                context['path_or_url'] = url
                user_states[user_id] = (STATE_WAITING_CATEGORY, context)
                
                # Ask user to select category
                await show_category_selection(client, event, user_id)
                return
            
            # Check if it's a video file
            elif event.media:
                try:
                    logger.info(f"Media received, type: {type(event.media)}")
                    logger.info(f"Media attributes: {dir(event.media)}")
                    
                    # Handle webpage preview (MessageMediaWebPage) type - extract URL
                    if hasattr(event.media, 'webpage'):
                        logger.info(f"MessageMediaWebPage detected, extracting URL")
                        
                        # Check if we have a valid URL in the message text
                        if event.text and is_valid_url(event.text.strip()):
                            url = event.text.strip()
                            logger.info(f"Valid URL extracted from webpage preview: {url}")
                            
                            # Save link and move to category selection
                            context['type'] = 'link'
                            context['path_or_url'] = url
                            user_states[user_id] = (STATE_WAITING_CATEGORY, context)
                            
                            # Ask user to select category
                            await show_category_selection(client, event, user_id)
                            return
                        # Check if the webpage has a URL we can use
                        elif hasattr(event.media.webpage, 'url') and event.media.webpage.url:
                            url = event.media.webpage.url
                            logger.info(f"Valid URL extracted from webpage object: {url}")
                            
                            # Save link and move to category selection
                            context['type'] = 'link'
                            context['path_or_url'] = url
                            user_states[user_id] = (STATE_WAITING_CATEGORY, context)
                            
                            # Ask user to select category
                            await show_category_selection(client, event, user_id)
                            return
                        else:
                            logger.warning("Could not extract a valid URL from webpage preview")
                            await event.respond(
                                "❌ **Invalid Link**\n\n"
                                "Could not extract a valid URL from the webpage preview.",
                                buttons=[Button.inline("Cancel", data="back_to_videos")]
                            )
                            return
                    
                    # Handle document type (video file)
                    if hasattr(event.media, 'document'):
                        logger.info(f"Document detected, mime_type: {event.media.document.mime_type if hasattr(event.media.document, 'mime_type') else 'unknown'}")
                        
                        if hasattr(event.media.document, 'mime_type') and event.media.document.mime_type.startswith('video/'):
                            logger.info("Valid video file detected, proceeding to download")
                            await event.respond("📥 Downloading video... Please wait.")
                            
                            # Save the video file
                            try:
                                video_path, thumbnail_path = await save_video_file(client, event)
                                logger.info(f"Video saved to: {video_path}, thumbnail: {thumbnail_path}")
                                
                                if not video_path:
                                    logger.error("Failed to save video file, path is None")
                                    await event.respond(
                                        "❌ **Error Saving File**\n\n"
                                        "Failed to save video file. Please try again.",
                                        buttons=[Button.inline("Cancel", data="back_to_videos")]
                                    )
                                    return
                                
                                # Save video path and move to category selection
                                context['type'] = 'file'
                                context['path_or_url'] = video_path
                                context['thumbnail_path'] = thumbnail_path
                                user_states[user_id] = (STATE_WAITING_CATEGORY, context)
                                logger.info(f"Video successfully processed, moving to category selection")
                                
                                # Ask user to select category
                                await show_category_selection(client, event, user_id)
                                return
                            except Exception as e:
                                logger.error(f"Exception during video save: {str(e)}")
                                logger.error(traceback.format_exc())
                                await event.respond(
                                    f"❌ **Error Saving Video**\n\n"
                                    f"Error details: {str(e)}",
                                    buttons=[Button.inline("Cancel", data="back_to_videos")]
                                )
                                return
                        else:
                            logger.warning("Media is not a video file or mime_type attribute missing")
                            await event.respond(
                                "❌ **Invalid File**\n\n"
                                "Please send a valid video file.",
                                buttons=[Button.inline("Cancel", data="back_to_videos")]
                            )
                            return
                    else:
                        logger.warning("Media doesn't have document attribute")
                        await event.respond(
                            "❌ **Link Processing Issue**\n\n"
                            "If you're sharing a link, please copy and paste the URL directly in a message instead of using link previews or embedded content.\n\n"
                            "For example, just type or paste: https://www.youtube.com/watch?v=example",
                            buttons=[Button.inline("Cancel", data="back_to_videos")]
                        )
                        return
                except Exception as e:
                    logger.error(f"Unexpected error processing media: {str(e)}")
                    logger.error(traceback.format_exc())
                    await event.respond(
                        f"❌ **Unexpected Error**\n\n"
                        f"Error details: {str(e)}",
                        buttons=[Button.inline("Cancel", data="back_to_videos")]
                    )
                    return
            else:
                logger.warning(f"Invalid input: neither text nor media")
                await event.respond(
                    "❌ **Invalid Input**\n\n"
                    "Please send either a video file or a video link.",
                    buttons=[Button.inline("Cancel", data="back_to_videos")]
                )


async def show_category_selection(client, event, user_id):
    """Show category selection for adding a video."""
    # Fetch all categories
    categories = database.get_all_categories()
    
    if not categories:
        await event.respond(
            "❌ **No categories found**\n\n"
            "Please add a category first.",
            buttons=[Button.inline("🔙 Back", data="menu_manage_videos")]
        )
        # Clear user state
        if user_id in user_states:
            del user_states[user_id]
        return
    
    # Create buttons for each category
    buttons = [
        [Button.inline(f"{cat['name']}", data=f"select_category_{cat['id']}")] 
        for cat in categories
    ]
    buttons.append([Button.inline("Cancel", data="back_to_videos")])
    
    await event.respond(
        "📁 **Select Category**\n\n"
        "Please select a category for this video:",
        buttons=buttons
    ) 