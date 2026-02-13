"""Utility functions shared across cogs."""

import random
from datetime import datetime

import discord

import bot as shared


def get_excluded_channels():
    """Get excluded channel IDs from config."""
    return set(shared.config.get("channels.excluded", []))


def get_troll_channels(guild):
    """Get text channels that aren't excluded from trolling."""
    excluded = get_excluded_channels()
    return [c for c in guild.text_channels if c.id not in excluded]


def get_online_members(guild):
    """Get non-bot online members."""
    return [m for m in guild.members if not m.bot and m.status != discord.Status.offline]


def pick_member(members, recent_victim_ids):
    """Pick a random member, preferring those not recently targeted.

    Falls back to pure random if all members are in the recent list.
    """
    if not members:
        return None
    fresh = [m for m in members if m.id not in recent_victim_ids]
    return random.choice(fresh) if fresh else random.choice(members)


def is_late_night():
    """Check if it's between midnight and 5am EAT."""
    hour = datetime.now(shared.EAT).hour
    start = shared.config.get("feature.late_night.start_hour", 0)
    end = shared.config.get("feature.late_night.end_hour", 5)
    return start <= hour < end


def get_channel_by_key(key):
    """Get a Discord channel by config key."""
    channel_id = shared.config.get(key)
    if channel_id:
        try:
            return shared.client.get_channel(int(channel_id))
        except (ValueError, TypeError):
            return None
    return None
