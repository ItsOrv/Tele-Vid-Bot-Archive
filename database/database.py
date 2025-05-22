#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Database operations module."""

import os
import sqlite3
import logging
import time
from contextlib import contextmanager
from config import config

logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with required tables if they don't exist."""
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table for access control
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    access_until INTEGER,
                    UNIQUE(id)
                )
            ''')
            
            # Create categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            ''')
            
            # Create videos table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    type TEXT NOT NULL,
                    path_or_url TEXT NOT NULL,
                    category_id INTEGER,
                    thumbnail_path TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE CASCADE
                )
            ''')
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            conn.commit()
            logger.info("Database initialized successfully")
    except sqlite3.Error as e:
        logger.error(f"Error initializing database: {e}")
        raise


@contextmanager
def get_connection():
    """Context manager for database connections."""
    connection = None
    try:
        connection = sqlite3.connect(config.DB_PATH)
        connection.row_factory = sqlite3.Row
        yield connection
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if connection:
            connection.close()


# User operations
def get_user(user_id):
    """Get user from database by ID."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Error getting user: {e}")
        return None


def save_user_access(user_id, username, expires_in=config.ACCESS_TIMEOUT):
    """Save or update user with access expiration time."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            access_until = int(time.time()) + expires_in
            cursor.execute(
                """INSERT OR REPLACE INTO users (id, username, access_until) 
                   VALUES (?, ?, ?)""",
                (user_id, username, access_until)
            )
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving user access: {e}")
        return False


def check_user_access(user_id):
    """Check if user has valid access."""
    user = get_user(user_id)
    if not user:
        return False
    
    current_time = int(time.time())
    return user["access_until"] > current_time


# Category operations
def get_all_categories():
    """Get all categories."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error getting categories: {e}")
        return []


def add_category(name):
    """Add a new category."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error adding category: {e}")
        return None


def delete_category(category_id):
    """Delete a category and all associated videos."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all videos in this category to delete files
            cursor.execute("SELECT * FROM videos WHERE category_id = ?", (category_id,))
            videos = cursor.fetchall()
            
            # Delete the category (cascade will delete videos from the database)
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            
            conn.commit()
            return videos  # Return videos for file deletion outside DB transaction
    except sqlite3.Error as e:
        logger.error(f"Error deleting category: {e}")
        return []


# Video operations
def add_video(title, video_type, path_or_url, category_id, thumbnail_path=None):
    """Add a new video."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO videos 
                   (title, type, path_or_url, category_id, thumbnail_path) 
                   VALUES (?, ?, ?, ?, ?)""",
                (title, video_type, path_or_url, category_id, thumbnail_path)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as e:
        logger.error(f"Error adding video: {e}")
        return None


def get_videos_by_category(category_id):
    """Get all videos in a category."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM videos WHERE category_id = ? ORDER BY title", 
                (category_id,)
            )
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error getting videos by category: {e}")
        return []


def get_video(video_id):
    """Get a specific video."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Error getting video: {e}")
        return None


def delete_video(video_id):
    """Delete a video."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
            video = cursor.fetchone()
            
            cursor.execute("DELETE FROM videos WHERE id = ?", (video_id,))
            conn.commit()
            
            return video  # Return video details for file deletion outside DB transaction
    except sqlite3.Error as e:
        logger.error(f"Error deleting video: {e}")
        return None 