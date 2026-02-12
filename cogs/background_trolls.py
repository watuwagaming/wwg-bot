"""Background troll functions and troll loop task."""

import asyncio
import random
from collections import deque
from datetime import datetime

import discord
from discord.ext import commands, tasks

import bot as shared
from helpers import get_online_members, get_channel_by_key
from messages import (
    jumpscare_messages, funny_nicknames, wrong_channel_messages,
    fake_mod_reasons, drama_templates, conspiracy_templates,
    afk_check_messages, random_polls, misquotes, fake_announcements,
    hype_messages, friday_messages,
)


class BackgroundTrolls(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = deque(maxlen=50)
        self.troll_loop.start()

    async def cog_unload(self):
        self.troll_loop.cancel()

    # --- Background Troll Functions ---

    async def jumpscare_ping(self, guild):
        """Randomly ping someone with something unhinged."""
        members = get_online_members(guild)
        channel = get_channel_by_key("channels.general_id")
        if not members or not channel:
            return
        victim = random.choice(members)
        msg = random.choice(jumpscare_messages)
        await channel.send(f"{victim.mention} {msg}")
        try:
            await shared.logger.log_troll("jumpscare_ping", "Jumpscare Ping", target_user=victim, channel=channel)
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def this_you(self, guild):
        """Repost a cached message with 'this you?'"""
        if not self.message_cache:
            return
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        author_id, content, _ = random.choice(self.message_cache)
        member = guild.get_member(author_id)
        if not member:
            return
        await channel.send(f"{member.mention} this you?\n> {content}")
        try:
            await shared.logger.log_troll("this_you", "This You?", target_user=member, channel=channel, details={"quoted": content[:100]})
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def rename_roulette(self, guild):
        """Give a random online member a funny nickname for 10 minutes."""
        members = get_online_members(guild)
        channel = get_channel_by_key("channels.general_id")
        if not members or not channel:
            return
        victim = random.choice(members)
        nickname = random.choice(funny_nicknames)
        try:
            old_nick = victim.nick
            await victim.edit(nick=nickname)
            await channel.send(
                f"\U0001f3b0 **RENAME ROULETTE** \U0001f3b0\n{victim.mention} is now **{nickname}** for the next 10 minutes!"
            )
            try:
                await shared.logger.log_troll("rename_roulette", "Rename Roulette", target_user=victim, channel=channel, details={"nickname": nickname})
                await shared.logger.increment_stat("trolls_bg_triggered")
            except Exception:
                pass
            await asyncio.sleep(600)
            await victim.edit(nick=old_nick)
        except discord.Forbidden:
            pass

    async def vibe_check(self, guild):
        """Post a vibe check -- a random reactor gets a funny nickname."""
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        msg = await channel.send("**VIBE CHECK** \U0001faf5\nReact to this... if you dare.")
        await msg.add_reaction("\u2705")

        await asyncio.sleep(60)

        msg = await channel.fetch_message(msg.id)
        reactors = []
        for reaction in msg.reactions:
            async for user in reaction.users():
                if user != self.bot.user and isinstance(user, discord.Member):
                    reactors.append(user)

        if not reactors:
            await channel.send("Nobody reacted... cowards. \U0001f414")
            return

        victim = random.choice(reactors)
        nickname = random.choice(funny_nicknames)
        try:
            old_nick = victim.nick
            await victim.edit(nick=nickname)
            await channel.send(f"{victim.mention} fell for it! Enjoy being **{nickname}** for 10 minutes \U0001f62d")
            try:
                await shared.logger.log_troll("vibe_check", "Vibe Check", target_user=victim, channel=channel, details={"nickname": nickname})
                await shared.logger.increment_stat("trolls_bg_triggered")
            except Exception:
                pass
            await asyncio.sleep(600)
            await victim.edit(nick=old_nick)
        except discord.Forbidden:
            pass

    async def wrong_channel(self, guild):
        """Post 'oops wrong channel' then delete it after a minute."""
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        msg = await channel.send(random.choice(wrong_channel_messages))
        try:
            await shared.logger.log_troll("wrong_channel", "Wrong Channel", channel=channel)
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass
        await asyncio.sleep(60)
        try:
            await msg.delete()
        except discord.NotFound:
            pass

    async def fake_mod_action(self, guild):
        """Post a fake warning for a random member."""
        members = get_online_members(guild)
        channel = get_channel_by_key("channels.general_id")
        if not members or not channel:
            return
        victim = random.choice(members)
        reason = random.choice(fake_mod_reasons)
        await channel.send(f"\u26a0\ufe0f **WARNING:** {victim.mention} has been warned for **{reason}**.")
        try:
            await shared.logger.log_troll("fake_mod_action", "Fake Mod Action", target_user=victim, channel=channel, details={"reason": reason})
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def server_drama(self, guild):
        """Create fake beef between two random members."""
        members = get_online_members(guild)
        channel = get_channel_by_key("channels.general_id")
        if len(members) < 2 or not channel:
            return
        a, b = random.sample(members, 2)
        template = random.choice(drama_templates)
        await channel.send(template.format(a=a.mention, b=b.mention))
        try:
            await shared.logger.log_troll("server_drama", "Server Drama", channel=channel, details={"users": [a.display_name, b.display_name]})
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def afk_check(self, guild):
        """Ping an online member asking if they're alive."""
        members = get_online_members(guild)
        channel = get_channel_by_key("channels.general_id")
        if not members or not channel:
            return
        victim = random.choice(members)
        msg = random.choice(afk_check_messages).format(user=victim.mention)
        await channel.send(msg)
        try:
            await shared.logger.log_troll("afk_check", "AFK Check", target_user=victim, channel=channel)
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def random_poll(self, guild):
        """Post an absurd poll."""
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        question, options = random.choice(random_polls)
        number_emojis = ["1\ufe0f\u20e3", "2\ufe0f\u20e3", "3\ufe0f\u20e3", "4\ufe0f\u20e3"]
        text = f"\U0001f4ca **POLL:** {question}\n"
        for i, option in enumerate(options):
            text += f"{number_emojis[i]} {option}\n"
        msg = await channel.send(text)
        for i in range(len(options)):
            await msg.add_reaction(number_emojis[i])
        try:
            await shared.logger.log_troll("random_poll", "Random Poll", channel=channel, details={"question": question})
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def motivational_misquote(self, guild):
        """Post a misattributed inspirational quote."""
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        quote, attribution = random.choice(misquotes)
        await channel.send(f"\U0001f4a1 **Inspirational Quote of the Day**\n\n*{quote}*\n{attribution}")
        try:
            await shared.logger.log_troll("motivational_misquote", "Motivational Misquote", channel=channel)
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def fake_announcement(self, guild):
        """Post something dramatic, edit it to 'jk' after a minute."""
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        msg = await channel.send(random.choice(fake_announcements))
        try:
            await shared.logger.log_troll("fake_announcement", "Fake Announcement", channel=channel)
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass
        await asyncio.sleep(60)
        try:
            await msg.edit(content=f"{msg.content}\n\n*jk lol*")
        except discord.NotFound:
            pass

    async def conspiracy_theory(self, guild):
        """Post an unhinged theory about a random member."""
        members = get_online_members(guild)
        channel = get_channel_by_key("channels.general_id")
        if not members or not channel:
            return
        victim = random.choice(members)
        theory = random.choice(conspiracy_templates).format(user=victim.mention)
        await channel.send(f"\U0001f9f5 **THREAD:** {theory}")
        try:
            await shared.logger.log_troll("conspiracy_theory", "Conspiracy Theory", target_user=victim, channel=channel)
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def hype_man(self, guild):
        """Randomly shout out a member for no reason."""
        members = get_online_members(guild)
        channel = get_channel_by_key("channels.general_id")
        if not members or not channel:
            return
        victim = random.choice(members)
        msg = random.choice(hype_messages).format(user=victim.mention)
        await channel.send(msg)
        try:
            await shared.logger.log_troll("hype_man", "Hype Man", target_user=victim, channel=channel)
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    async def friday_hype(self, guild):
        """Post a Friday hype message (only fires on Fridays)."""
        if datetime.now(shared.EAT).weekday() != 4:
            return
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        await channel.send(random.choice(friday_messages))
        try:
            await shared.logger.log_troll("friday_hype", "Friday Hype", channel=channel)
            await shared.logger.increment_stat("trolls_bg_triggered")
        except Exception:
            pass

    def _get_background_trolls(self):
        """Return list of (method, config_name) tuples."""
        return [
            (self.jumpscare_ping, "jumpscare_ping"),
            (self.this_you, "this_you"),
            (self.rename_roulette, "rename_roulette"),
            (self.vibe_check, "vibe_check"),
            (self.wrong_channel, "wrong_channel"),
            (self.fake_mod_action, "fake_mod_action"),
            (self.server_drama, "server_drama"),
            (self.afk_check, "afk_check"),
            (self.random_poll, "random_poll"),
            (self.motivational_misquote, "motivational_misquote"),
            (self.fake_announcement, "fake_announcement"),
            (self.conspiracy_theory, "conspiracy_theory"),
            (self.hype_man, "hype_man"),
            (self.friday_hype, "friday_hype"),
        ]

    @tasks.loop()
    async def troll_loop(self):
        """Periodic troll events -- runs at random intervals."""
        if not shared.config.get("feature.troll_loop.enabled", True):
            await asyncio.sleep(60)
            return
        if not self.bot.guilds:
            return
        guild = self.bot.guilds[0]

        # Filter to only enabled background trolls
        enabled = [(fn, name) for fn, name in self._get_background_trolls()
                    if shared.config.get(f"bg_troll.{name}.enabled", True)]
        if enabled:
            troll_fn, troll_name = random.choice(enabled)
            await troll_fn(guild)

        # Weekend/Friday: more frequent, otherwise longer
        day = datetime.now(shared.EAT).weekday()
        if day in (4, 5, 6):
            min_h = shared.config.get("feature.troll_loop.weekend_min_hours", 0.5)
            max_h = shared.config.get("feature.troll_loop.weekend_max_hours", 2.0)
        else:
            min_h = shared.config.get("feature.troll_loop.weekday_min_hours", 1.0)
            max_h = shared.config.get("feature.troll_loop.weekday_max_hours", 4.0)
        wait_hours = random.uniform(min_h, max_h)
        await asyncio.sleep(wait_hours * 3600)

    @troll_loop.before_loop
    async def before_troll_loop(self):
        await self.bot.wait_until_ready()
        delay_min = shared.config.get("feature.troll_loop.initial_delay_min", 300)
        delay_max = shared.config.get("feature.troll_loop.initial_delay_max", 1800)
        await asyncio.sleep(random.randint(delay_min, delay_max))


async def setup(bot):
    await bot.add_cog(BackgroundTrolls(bot))
