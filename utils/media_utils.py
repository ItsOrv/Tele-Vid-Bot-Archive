#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Media utilities for handling video files and thumbnails."""

import os
import uuid
import logging
import asyncio
import traceback
from telethon import types
import cv2
from config import config

logger = logging.getLogger(__name__)

async def save_video_file(client, message):
    """
    Save a video file received from user.
    
    Args:
        client: Telethon client
        message: Message containing the video
        
    Returns:
        tuple: (file_path, thumbnail_path) or (None, None) on failure
    """
    try:
        logger.info(f"Starting to save video file from message with ID: {message.id}")
        logger.info(f"Message attributes: {dir(message)}")
        
        # Generate unique filename
        video_filename = f"{uuid.uuid4().hex}.mp4"
        video_path = os.path.join(config.VIDEO_DIR, video_filename)
        logger.info(f"Generated video path: {video_path}")
        
        # Check if we have a media document
        if hasattr(message, 'media') and hasattr(message.media, 'document'):
            document = message.media.document
            logger.info(f"Document found, MIME type: {getattr(document, 'mime_type', 'unknown')}")
            
            if hasattr(document, 'mime_type') and document.mime_type.startswith('video/'):
                logger.info("Valid video MIME type detected")
                try:
                    # Download media
                    logger.info(f"Starting download to {video_path}")
                    downloaded_path = await client.download_media(message.media, video_path)
                    logger.info(f"Downloaded to: {downloaded_path}")
                    
                    if not downloaded_path or not os.path.exists(downloaded_path):
                        logger.error(f"Download failed - file not found at {downloaded_path}")
                        return None, None
                        
                    # Generate thumbnail
                    logger.info("Generating thumbnail")
                    thumbnail_path = await generate_thumbnail(downloaded_path)
                    
                    logger.info(f"Video successfully saved to {downloaded_path}, thumbnail: {thumbnail_path}")
                    return downloaded_path, thumbnail_path
                except Exception as e:
                    logger.error(f"Error during download: {str(e)}")
                    logger.error(traceback.format_exc())
                    return None, None
            else:
                logger.error(f"Invalid MIME type: {getattr(document, 'mime_type', 'unknown')}")
                return None, None
        else:
            logger.error("Message does not contain media.document")
            return None, None
    except Exception as e:
        logger.error(f"Error in save_video_file: {str(e)}")
        logger.error(traceback.format_exc())
        return None, None


async def generate_thumbnail(video_path):
    """
    Generate thumbnail from video file.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        str: Path to the thumbnail or None on failure
    """
    try:
        logger.info(f"Starting thumbnail generation for video: {video_path}")
        
        if not os.path.exists(video_path):
            logger.error(f"Video file doesn't exist at {video_path}")
            return None
            
        thumbnail_filename = f"{os.path.basename(video_path)}.jpg"
        thumbnail_path = os.path.join(config.THUMBNAIL_DIR, thumbnail_filename)
        logger.info(f"Target thumbnail path: {thumbnail_path}")
        
        # Use OpenCV to extract a frame from the middle of the video
        def _generate():
            try:
                logger.info("Opening video with OpenCV")
                vidcap = cv2.VideoCapture(video_path)
                
                if not vidcap.isOpened():
                    logger.error("Failed to open video file with OpenCV")
                    return None
                
                # Get total frames
                total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
                logger.info(f"Total frames: {total_frames}")
                
                if total_frames == 0:
                    logger.error("Video has 0 frames")
                    return None
                
                # Set position to the middle frame
                middle_frame = total_frames // 2
                logger.info(f"Setting position to middle frame: {middle_frame}")
                vidcap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
                
                # Read the frame
                success, image = vidcap.read()
                if not success:
                    logger.error("Failed to read middle frame")
                    return None
                
                logger.info("Successfully read middle frame")
                    
                # Resize image if needed (keeping aspect ratio)
                height, width = image.shape[:2]
                logger.info(f"Original image dimensions: {width}x{height}")
                
                max_dim = 320  # Telegram thumbnail size
                
                if height > width:
                    new_height, new_width = max_dim, int(max_dim * width / height)
                else:
                    new_height, new_width = int(max_dim * height / width), max_dim
                
                logger.info(f"Resizing to: {new_width}x{new_height}")
                resized_image = cv2.resize(image, (new_width, new_height))
                
                # Save the thumbnail
                logger.info(f"Saving thumbnail to: {thumbnail_path}")
                result = cv2.imwrite(thumbnail_path, resized_image)
                
                if not result:
                    logger.error("Failed to save thumbnail image")
                    return None
                    
                logger.info("Thumbnail saved successfully")
                vidcap.release()
                return thumbnail_path
            except Exception as e:
                logger.error(f"Error in _generate: {str(e)}")
                logger.error(traceback.format_exc())
                return None
            
        # Run in a thread pool to avoid blocking
        logger.info("Running thumbnail generation in a thread pool")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _generate)
        
        if result:
            logger.info(f"Thumbnail generated successfully at {result}")
        else:
            logger.error("Thumbnail generation failed")
            
        return result
    except Exception as e:
        logger.error(f"Error in generate_thumbnail: {str(e)}")
        logger.error(traceback.format_exc())
        return None


def is_valid_url(url):
    """
    Check if the URL is a valid URL format.
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Add http:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Accept almost any URL format - only basic check that it has some content
        if len(url) < 5:  # Minimum possible URL would be like "h://x"
            logger.warning(f"URL too short: {url}")
            return False
            
        # Accept any domain and format
        logger.info(f"URL validation for '{url}': True (all restrictions removed)")
        return True
    except Exception as e:
        logger.error(f"Error validating URL: {str(e)}")
        logger.error(traceback.format_exc())
        return False


def delete_video_files(video):
    """
    Delete video and thumbnail files from disk.
    
    Args:
        video: Video record from database
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Attempting to delete video files for video ID: {video['id']}")
        
        # Only delete if it's a file type
        if video["type"] != "file":
            logger.info("Video is not a file type, no files to delete")
            return True
            
        # Delete video file if exists
        video_path = video["path_or_url"]
        if os.path.exists(video_path):
            logger.info(f"Deleting video file: {video_path}")
            os.remove(video_path)
        else:
            logger.warning(f"Video file not found at: {video_path}")
            
        # Delete thumbnail if exists
        thumbnail_path = video["thumbnail_path"]
        if thumbnail_path and os.path.exists(thumbnail_path):
            logger.info(f"Deleting thumbnail: {thumbnail_path}")
            os.remove(thumbnail_path)
        elif thumbnail_path:
            logger.warning(f"Thumbnail not found at: {thumbnail_path}")
            
        logger.info("Video files deleted successfully")
        return True
    except Exception as e:
        logger.error(f"Error deleting video files: {str(e)}")
        logger.error(traceback.format_exc())
        return False 