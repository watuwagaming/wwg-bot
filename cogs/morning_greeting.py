"""Morning greeting task loop."""

import asyncio
import random
from datetime import timedelta

from discord.ext import commands, tasks

import bot as shared
from helpers import get_channel_by_key
from messages import morning_greetings


async def wait_until_morning():
    """Calculate seconds to wait until a random morning time (6am-11am GMT+3)."""
    from datetime import datetime
    now = datetime.now(shared.EAT)
    hour_min = shared.config.get("feature.morning_greeting.hour_min", 6)
    hour_max = shared.config.get("feature.morning_greeting.hour_max", 10)
    random_hour = random.randint(hour_min, hour_max)
    random_minute = random.randint(0, 59)
    target = now.replace(hour=random_hour, minute=random_minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()


class MorningGreeting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.morning_greeting.start()

    async def cog_unload(self):
        self.morning_greeting.cancel()

    @tasks.loop(hours=24)
    async def morning_greeting(self):
        if not shared.config.get("feature.morning_greeting.enabled", True):
            return
        channel = get_channel_by_key("channels.greetings_id")
        if channel:
            greeting = random.choice(morning_greetings)
            await channel.send(greeting)
            try:
                await shared.logger.log_activity("greeting", "Sent morning greeting", channel=channel)
                await shared.logger.increment_stat("greetings_sent")
            except Exception:
                pass

    @morning_greeting.before_loop
    async def before_morning_greeting(self):
        await self.bot.wait_until_ready()
        wait_seconds = await wait_until_morning()
        await asyncio.sleep(wait_seconds)


async def setup(bot):
    await bot.add_cog(MorningGreeting(bot))
