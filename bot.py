"""Shared bot instance and global references used by all cogs."""

import discord
import pytz
from discord.ext import commands

intents = discord.Intents.all()
client = commands.Bot(command_prefix="$", intents=intents)

# Populated in on_ready (main.py)
config = None   # BotConfig
logger = None   # BotLogger

EAT = pytz.timezone("Africa/Nairobi")  # GMT+3
