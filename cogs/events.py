"""Event listeners: on_member_join, on_presence_update, on_typing, on_reaction_add."""

import asyncio
import random
from datetime import datetime

import discord
from discord.ext import commands, tasks

import bot as shared
from helpers import get_excluded_channels, get_online_members, get_channel_by_key
from messages import funny_nicknames, fake_rules, welcome_messages, typing_callout_messages


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.game_notify_cooldown = {}      # {game_name: datetime}
        self.game_user_ping_cooldown = {}   # {user_id: datetime}
        self.typing_tracker = {}            # {(channel_id, user_id): datetime}
        self.cleanup_loop.start()

    async def cog_unload(self):
        self.cleanup_loop.cancel()

    @tasks.loop(hours=1)
    async def cleanup_loop(self):
        """Purge expired entries from cooldown dicts to prevent memory leaks."""
        now = datetime.now(shared.EAT)

        # Clean typing tracker (entries older than stale_sec)
        stale = shared.config.get("feature.typing_callout.stale_sec", 120) if shared.config else 120
        stale_keys = [k for k, v in self.typing_tracker.items() if (now - v).total_seconds() > stale]
        for k in stale_keys:
            del self.typing_tracker[k]

        # Clean game cooldowns (entries older than their cooldown period)
        game_cd = shared.config.get("feature.game_detection.game_cooldown_sec", 86400) if shared.config else 86400
        expired_games = [g for g, t in self.game_notify_cooldown.items() if (now - t).total_seconds() > game_cd * 2]
        for g in expired_games:
            del self.game_notify_cooldown[g]

        user_cd = shared.config.get("feature.game_detection.user_cooldown_sec", 86400) if shared.config else 86400
        expired_users = [u for u, t in self.game_user_ping_cooldown.items() if (now - t).total_seconds() > user_cd * 2]
        for u in expired_users:
            del self.game_user_ping_cooldown[u]

    @cleanup_loop.before_loop
    async def before_cleanup_loop(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Welcome hazing -- give new members a ridiculous nickname and a fake rule."""
        if member.bot:
            return
        if not shared.config.get("feature.welcome_hazing.enabled", True):
            return
        chance = shared.config.get("feature.welcome_hazing.chance", 0.20)
        if random.random() > chance:
            return
        channel = get_channel_by_key("channels.general_id")
        if not channel:
            return
        nickname = random.choice(funny_nicknames)
        rule = random.choice(fake_rules)
        rule_num = random.randint(47, 200)

        try:
            await member.edit(nick=nickname)
        except discord.Forbidden:
            nickname = None

        template = random.choice(welcome_messages)
        await channel.send(template.format(user=member.mention, nick=nickname or member.display_name, num=rule_num, rule=rule))

        try:
            await shared.logger.log_troll("welcome_hazing", "Welcome Hazing", target_user=member, channel=channel, details={"nickname": nickname, "rule": rule})
            await shared.logger.increment_stat("welcomes_sent")
        except Exception:
            pass

        # Revert nickname after random time
        if nickname:
            min_h = shared.config.get("feature.welcome_hazing.nick_revert_min_hours", 1.0)
            max_h = shared.config.get("feature.welcome_hazing.nick_revert_max_hours", 168.0)
            wait_hours = random.uniform(min_h, max_h)
            await asyncio.sleep(wait_hours * 3600)
            try:
                await member.edit(nick=None)
            except discord.Forbidden:
                return

            if wait_hours < 6:
                early_messages = [
                    f"fine {member.mention}, you can have your name back. I was feeling generous today.",
                    f"{member.mention} got lucky. I was gonna keep that name for WAY longer.",
                    f"giving {member.mention} their name back early because I'm in a good mood. Don't get used to it.",
                    f"{member.mention} you're free. That was just a taste of what I can do.",
                    f"releasing {member.mention} from nickname jail early. Good behavior I guess.",
                ]
                await channel.send(random.choice(early_messages))
            elif wait_hours > 120:
                late_messages = [
                    f"{member.mention} I almost forgot about you. Here's your name back... you earned it.",
                    f"oh right {member.mention} exists. My bad. Name restored I guess.",
                    f"after careful consideration (I forgot), {member.mention} can have their name back.",
                    f"{member.mention} served their full sentence. Welcome back to society.",
                    f"finally freeing {member.mention}. That nickname was growing on me though.",
                    f"{member.mention} has been released from nickname prison. It's been real.",
                ]
                await channel.send(random.choice(late_messages))
            else:
                normal_messages = [
                    f"{member.mention} alright your time is up. Name's back. You're welcome.",
                    f"restoring {member.mention}'s identity. Try not to get caught again.",
                    f"{member.mention} you survived. Name restored. Don't let it happen again.",
                    f"giving {member.mention} their name back. It was fun while it lasted.",
                ]
                await channel.send(random.choice(normal_messages))

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        """Detect when someone starts playing a game others are already on."""
        if after.bot:
            return
        if not shared.config.get("feature.game_detection.enabled", True):
            return

        before_games = {a.name for a in before.activities if a.type == discord.ActivityType.playing and a.name}
        after_games = {a.name for a in after.activities if a.type == discord.ActivityType.playing and a.name}
        new_games = after_games - before_games

        if not new_games:
            return

        now = datetime.now(shared.EAT)
        game_cooldown = shared.config.get("feature.game_detection.game_cooldown_sec", 86400)
        user_cooldown = shared.config.get("feature.game_detection.user_cooldown_sec", 86400)
        min_players = shared.config.get("feature.game_detection.min_players", 2)
        chance = shared.config.get("feature.game_detection.chance", 0.03)

        for game_name in new_games:
            # Cooldown: only notify once per game per configured period
            if game_name in self.game_notify_cooldown:
                if (now - self.game_notify_cooldown[game_name]).total_seconds() < game_cooldown:
                    continue

            # Find others playing the same game
            players = []
            for m in after.guild.members:
                if m == after or m.bot:
                    continue
                for a in m.activities:
                    if a.type == discord.ActivityType.playing and a.name == game_name:
                        players.append(m)
                        break

            if len(players) >= min_players and random.random() < chance:
                # Filter out players who were pinged recently
                eligible = [m for m in players if m.id not in self.game_user_ping_cooldown
                            or (now - self.game_user_ping_cooldown[m.id]).total_seconds() >= user_cooldown]
                # Also check the player who just started
                if after.id in self.game_user_ping_cooldown:
                    if (now - self.game_user_ping_cooldown[after.id]).total_seconds() < user_cooldown:
                        continue

                if not eligible:
                    continue

                msg = (
                    f"\U0001f440 {after.mention} just hopped on **{game_name}** \u2014 "
                    f"{', '.join(m.mention for m in eligible[:5])} "
                    f"{'are' if len(eligible) > 1 else 'is'} already on it. Link up?"
                )
                ch = get_channel_by_key("channels.gamers_arena_id")
                if ch:
                    await ch.send(msg)
                self.game_notify_cooldown[game_name] = now
                # Record cooldown for all pinged users
                self.game_user_ping_cooldown[after.id] = now
                for m in eligible[:5]:
                    self.game_user_ping_cooldown[m.id] = now

                try:
                    await shared.logger.log_activity("game_detect", f"{after.display_name} playing {game_name}", channel=ch, user=after, metadata={"players": [m.display_name for m in eligible[:5]]})
                    await shared.logger.increment_stat("game_detections")
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        """Typing callout -- if someone types for too long, call them out."""
        if user.bot:
            return
        if not hasattr(channel, "guild") or channel.guild is None:
            return
        if not shared.config.get("feature.typing_callout.enabled", True):
            return
        if channel.id in get_excluded_channels():
            return

        key = (channel.id, user.id)
        now = datetime.now(shared.EAT)
        duration = shared.config.get("feature.typing_callout.duration_sec", 60)
        stale = shared.config.get("feature.typing_callout.stale_sec", 120)
        chance = shared.config.get("feature.typing_callout.chance", 0.30)

        if key not in self.typing_tracker:
            self.typing_tracker[key] = now
        else:
            elapsed = (now - self.typing_tracker[key]).total_seconds()
            if elapsed >= duration and random.random() < chance:
                msg = random.choice(typing_callout_messages).format(user=user.mention)
                await channel.send(msg)
                del self.typing_tracker[key]
                try:
                    await shared.logger.log_troll("typing_callout", "Typing Callout", target_user=user, channel=channel)
                    await shared.logger.increment_stat("typing_callouts")
                except Exception:
                    pass
            elif elapsed > stale:
                del self.typing_tracker[key]

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """Reaction chain -- if 3+ people react the same emoji, bot piles on."""
        if user.bot:
            return
        if not shared.config.get("feature.reaction_chain.enabled", True):
            return
        threshold = shared.config.get("feature.reaction_chain.threshold", 3)
        # Count non-bot users with this reaction
        non_bot_count = 0
        bot_already = False
        async for reactor in reaction.users():
            if reactor.id == self.bot.user.id:
                bot_already = True
            elif not reactor.bot:
                non_bot_count += 1

        if non_bot_count >= threshold and not bot_already:
            try:
                await reaction.message.add_reaction(reaction.emoji)
                try:
                    await shared.logger.log_activity("reaction_chain", "Joined reaction chain", channel=reaction.message.channel)
                    await shared.logger.increment_stat("reaction_chains")
                except Exception:
                    pass
            except discord.HTTPException:
                pass


async def setup(bot):
    await bot.add_cog(Events(bot))
