"""Status rotation task loop."""

import asyncio
import random

import discord
from discord.ext import commands, tasks

import bot as shared
from helpers import get_online_members
from messages import games


class StatusRotation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rotate_status.start()

    async def cog_unload(self):
        self.rotate_status.cancel()

    @tasks.loop(count=1)
    async def rotate_status(self):
        while True:
            interval = shared.config.get("feature.status_rotation.interval_sec", 600) if shared.config else 600
            await asyncio.sleep(interval)

            if not shared.config.get("feature.status_rotation.enabled", True):
                continue
            mention_chance = shared.config.get("feature.status_rotation.member_mention_chance", 0.30)
            if self.bot.guilds and random.random() < mention_chance:
                members = get_online_members(self.bot.guilds[0])
                if members:
                    member = random.choice(members)
                    await self.bot.change_presence(
                        activity=discord.Game(name=f"with {member.display_name}")
                    )
                    try:
                        await shared.logger.log_activity("status_change", f"Playing with {member.display_name}")
                    except Exception:
                        pass
                    continue

            randomGame = random.choice(games)
            if randomGame[0] == discord.ActivityType.streaming:
                await self.bot.change_presence(
                    activity=discord.Streaming(
                        name="Watu wa Gaming", url=randomGame[1]
                    )
                )
            else:
                await self.bot.change_presence(
                    activity=discord.Activity(
                        type=randomGame[0],
                        name=randomGame[1],
                    )
                )

    @rotate_status.before_loop
    async def before_rotate_status(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(StatusRotation(bot))
