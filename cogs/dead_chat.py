"""Dead chat reviver task loop."""

import random
from datetime import datetime

from discord.ext import commands, tasks

import bot as shared
from helpers import get_channel_by_key, is_late_night
from messages import hot_takes, late_night_messages


class DeadChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_message_time = None
        self.dead_chat_loop.start()

    async def cog_unload(self):
        self.dead_chat_loop.cancel()

    @tasks.loop(minutes=30)
    async def dead_chat_loop(self):
        if not shared.config.get("feature.dead_chat.enabled", True):
            return
        if not self.bot.guilds or self.last_message_time is None:
            return
        now = datetime.now(shared.EAT)
        silence = (now - self.last_message_time).total_seconds()
        threshold = shared.config.get("feature.dead_chat.silence_threshold_sec", 7200)
        if silence < threshold:
            return
        chance = shared.config.get("feature.dead_chat.chance", 0.50)
        if random.random() > chance:
            return
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        if is_late_night():
            msg = random.choice(late_night_messages)
        else:
            msg = random.choice(hot_takes)
        await channel.send(msg)
        self.last_message_time = now  # Reset so it doesn't spam
        try:
            await shared.logger.log_activity("dead_chat", "Revived dead chat", channel=channel)
            await shared.logger.increment_stat("dead_chat_revives")
        except Exception:
            pass

    @dead_chat_loop.before_loop
    async def before_dead_chat_loop(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(DeadChat(bot))
