#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Handlers initialization module."""

from handlers.auth_handler import register_auth_handlers
from handlers.category_handler import register_category_handlers
from handlers.video_handler import register_video_handlers

async def register_handlers(client):
    """Register all handlers."""
    await register_auth_handlers(client)
    await register_category_handlers(client)
    await register_video_handlers(client) 