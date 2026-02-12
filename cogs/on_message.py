"""Main on_message handler: GN police, keyword detectors, per-message trolls, late night."""

import asyncio
import random
from collections import deque
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import bot as shared
from helpers import get_excluded_channels, is_late_night
from messages import (
    gn_phrases, gn_callouts, hype_detector_messages,
    cursed_emojis, fake_typing_messages, take_judgements,
    essay_responses, k_responses, late_night_messages,
)


class OnMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gn_watchlist = {}                  # {user_id: datetime}
        self.recent_message_times = deque(maxlen=200)
        self.hype_cooldown_until = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Skip DMs and modmail (handled by Modmail cog)
        if isinstance(message.channel, discord.DMChannel):
            return
        modmail_id = shared.config.get("channels.modmail_id", "")
        if modmail_id and message.channel.id == int(modmail_id) and message.reference:
            return

        # --- Track activity for dead chat reviver ---
        if message.guild:
            dead_chat_cog = self.bot.get_cog("DeadChat")
            if dead_chat_cog:
                dead_chat_cog.last_message_time = datetime.now(shared.EAT)

        # --- Count messages (batched) ---
        try:
            await shared.logger.count_message()
        except Exception:
            pass

        excluded = get_excluded_channels()

        try:
            # --- GN Police: check if sender previously said goodnight ---
            if shared.config.get("feature.gn_police.enabled", True) and message.guild and message.author.id in self.gn_watchlist:
                said_gn_at = self.gn_watchlist[message.author.id]
                mins = int((datetime.now(shared.EAT) - said_gn_at).total_seconds() / 60)
                min_mins = shared.config.get("feature.gn_police.min_minutes", 20)
                max_mins = shared.config.get("feature.gn_police.max_minutes", 180)
                gn_chance = shared.config.get("feature.gn_police.chance", 0.50)
                if min_mins <= mins <= max_mins and random.random() < gn_chance:
                    callout = random.choice(gn_callouts).format(user=message.author.mention, mins=mins)
                    await message.channel.send(callout)
                    del self.gn_watchlist[message.author.id]
                    try:
                        await shared.logger.log_troll("gn_police", "GN Police", target_user=message.author, channel=message.channel, details={"minutes": mins})
                        await shared.logger.increment_stat("gn_callouts")
                    except Exception:
                        pass
                elif mins > max_mins:
                    del self.gn_watchlist[message.author.id]

            # --- GN Police: detect goodnight messages ---
            if message.guild and message.content:
                lower = message.content.lower().strip()
                if any(lower == phrase or lower.startswith(phrase + " ") or lower.endswith(" " + phrase) for phrase in gn_phrases):
                    self.gn_watchlist[message.author.id] = datetime.now(shared.EAT)

            # --- Keyword Triggers (only one fires per message) ---
            keyword_triggered = False

            # --- Rage Detector ---
            if (not keyword_triggered and shared.config.get("feature.rage_detector.enabled", True)
                    and message.guild and message.content and message.channel.id not in excluded):
                content = message.content
                min_len = shared.config.get("feature.rage_detector.min_length", 10)
                caps_thresh = shared.config.get("feature.rage_detector.caps_threshold", 0.70)
                exclaim_thresh = shared.config.get("feature.rage_detector.exclaim_threshold", 3)
                rage_chance = shared.config.get("feature.rage_detector.chance", 0.35)
                is_caps_rage = len(content) >= min_len and sum(1 for c in content if c.isupper()) / max(len(content.replace(" ", "")), 1) > caps_thresh
                is_exclaim_rage = content.count("!") >= exclaim_thresh
                if (is_caps_rage or is_exclaim_rage) and random.random() < rage_chance:
                    rage_responses = [
                        "bro breathe. it's just a game.",
                        "I can feel the anger through the screen \U0001f480",
                        "somebody get this person some water",
                        "controller status: in danger",
                        "the caps lock is doing a lot of heavy lifting rn",
                        "deep breaths. in through the nose. out through the mouth.",
                        "this is a certified rage moment",
                        "I think {user} needs a break \U0001f62d",
                        "calm down before you break something",
                        "bro is HEATED. someone check on them.",
                    ]
                    resp = random.choice(rage_responses).format(user=message.author.mention)
                    await message.reply(resp, mention_author=False)
                    keyword_triggered = True
                    try:
                        await shared.logger.log_troll("rage_detector", "Rage Detector", target_user=message.author, channel=message.channel)
                        await shared.logger.increment_stat("rage_detections")
                    except Exception:
                        pass

            # --- Excuse Generator ---
            if (not keyword_triggered and shared.config.get("feature.excuse_generator.enabled", True)
                    and message.guild and message.content and message.channel.id not in excluded):
                lower = message.content.lower()
                loss_phrases = ["i lost", "we lost", "took an l", "got destroyed", "got clapped", "got wrecked", "got bodied", "lost the game"]
                excuse_chance = shared.config.get("feature.excuse_generator.chance", 0.40)
                if any(phrase in lower for phrase in loss_phrases) and random.random() < excuse_chance:
                    excuse_responses = [
                        "nah it was definitely lag",
                        "your controller was broken obviously",
                        "the sun was in your eyes. through the ceiling. it happens.",
                        "you were just warming up. the real game starts next round.",
                        "I blame the matchmaking tbh",
                        "the other team was clearly cheating. I ran the numbers.",
                        "your teammate sold you. not your fault.",
                        "that game doesn't count. I'm deleting it from the records.",
                        "you weren't even trying. we all know that.",
                        "it was rigged from the start honestly",
                    ]
                    await message.reply(random.choice(excuse_responses), mention_author=False)
                    keyword_triggered = True
                    try:
                        await shared.logger.log_troll("excuse_generator", "Excuse Generator", target_user=message.author, channel=message.channel)
                        await shared.logger.increment_stat("excuse_generations")
                    except Exception:
                        pass

            # --- Cap Alarm ---
            if (not keyword_triggered and shared.config.get("feature.cap_alarm.enabled", True)
                    and message.guild and message.content and message.channel.id not in excluded):
                lower = message.content.lower()
                cap_phrases = ["i swear", "no cap", "trust me", "on my life", "on god", "deadass", "fr fr", "i promise", "not lying"]
                cap_chance = shared.config.get("feature.cap_alarm.chance", 0.35)
                if any(phrase in lower for phrase in cap_phrases) and random.random() < cap_chance:
                    cap_responses = [
                        "\U0001f9e2\U0001f9e2\U0001f9e2",
                        "cap detected \U0001f6a8",
                        "the cap alarm is going off rn",
                        "idk bro that sounds like cap to me",
                        "my cap detector is going CRAZY right now",
                        "source: trust me bro",
                        "interesting... the lie detector determined that was cap",
                        "you said 'trust me' so now I trust you less",
                        "cap levels are off the charts \U0001f4c8",
                    ]
                    await message.reply(random.choice(cap_responses), mention_author=False)
                    keyword_triggered = True
                    try:
                        await shared.logger.log_troll("cap_alarm", "Cap Alarm", target_user=message.author, channel=message.channel)
                        await shared.logger.increment_stat("cap_alarms")
                    except Exception:
                        pass

            # --- Flex Police ---
            if (not keyword_triggered and shared.config.get("feature.flex_police.enabled", True)
                    and message.guild and message.content and message.channel.id not in excluded):
                lower = message.content.lower()
                flex_phrases = ["i'm the best", "im the best", "easy win", "easy dub", "too easy", "i carried", "they can't beat me", "i'm goated", "im goated", "undefeated", "no one can", "i don't lose", "i dont lose"]
                flex_chance = shared.config.get("feature.flex_police.chance", 0.40)
                if any(phrase in lower for phrase in flex_phrases) and random.random() < flex_chance:
                    flex_responses = [
                        "calm down it's not that serious \U0001f612",
                        "bro is flexing in a Discord server \U0001f480",
                        "someone humble this person please",
                        "screenshot this for when they lose next game",
                        "the ego on this one...",
                        "and then you woke up",
                        "bold words for someone in trolling distance",
                        "saved this message for later. you know, for when you lose.",
                        "ok champ. we'll see about that.",
                        "this is going on the wall of shame if you lose tonight",
                    ]
                    await message.reply(random.choice(flex_responses), mention_author=False)
                    keyword_triggered = True
                    try:
                        await shared.logger.log_troll("flex_police", "Flex Police", target_user=message.author, channel=message.channel)
                        await shared.logger.increment_stat("flex_polices")
                    except Exception:
                        pass

            # --- Lag Defender ---
            if (not keyword_triggered and shared.config.get("feature.lag_defender.enabled", True)
                    and message.guild and message.content and message.channel.id not in excluded):
                lower = message.content.lower()
                lag_chance = shared.config.get("feature.lag_defender.chance", 0.40)
                if "lag" in lower.split() and random.random() < lag_chance:
                    lag_responses = [
                        "IT WAS DEFINITELY LAG. I believe you.",
                        "100% lag. No way that was a skill issue. Absolutely not.",
                        "I checked the servers and yeah it was lagging. Trust me.",
                        "lag is undefeated honestly",
                        "they need to fix these servers fr fr",
                        "I SAW the lag. You would've won if it wasn't for the lag.",
                        "the lag was crazy just now ngl",
                        "lag diff. nothing else to say.",
                        "bro was about to go crazy but the lag said no \U0001f480",
                    ]
                    await message.reply(random.choice(lag_responses), mention_author=False)
                    keyword_triggered = True
                    try:
                        await shared.logger.log_troll("lag_defender", "Lag Defender", target_user=message.author, channel=message.channel)
                        await shared.logger.increment_stat("lag_defenses")
                    except Exception:
                        pass

            # --- Hype Detector ---
            if shared.config.get("feature.hype_detector.enabled", True) and message.guild and message.channel.id not in excluded:
                now = datetime.now(shared.EAT)
                self.recent_message_times.append(now)
                time_window = shared.config.get("feature.hype_detector.time_window_sec", 60)
                recent_count = sum(1 for t in self.recent_message_times if (now - t).total_seconds() < time_window)
                threshold = shared.config.get("feature.hype_detector.threshold_messages", 15)
                day = datetime.now(shared.EAT).weekday()
                hype_chance = shared.config.get("feature.hype_detector.weekend_chance", 0.08) if day in (4, 5, 6) else shared.config.get("feature.hype_detector.weekday_chance", 0.05)
                cooldown_min = shared.config.get("feature.hype_detector.cooldown_min", 30)
                if recent_count >= threshold and (self.hype_cooldown_until is None or now > self.hype_cooldown_until) and random.random() < hype_chance:
                    await message.channel.send(random.choice(hype_detector_messages))
                    self.hype_cooldown_until = now + timedelta(minutes=cooldown_min)
                    try:
                        await shared.logger.log_troll("hype_detector", "Hype Detector", channel=message.channel, details={"message_count": recent_count})
                        await shared.logger.increment_stat("hype_detections")
                    except Exception:
                        pass

            # --- Troll checks (only in non-excluded guild channels) ---
            if message.guild and message.channel.id not in excluded:

                # Silently cache messages for "this you?" feature
                bg_trolls_cog = self.bot.get_cog("BackgroundTrolls")
                cache_chance = shared.config.get("feature.message_cache.chance", 0.10)
                if message.content and len(message.content) > 10 and random.random() < cache_chance:
                    if bg_trolls_cog:
                        bg_trolls_cog.message_cache.append((message.author.id, message.content, message.channel.id))

                # Essay detector
                troll_fired = False
                if shared.config.get("feature.essay_detector.enabled", True):
                    essay_thresh = shared.config.get("feature.essay_detector.threshold_chars", 500)
                    essay_chance = shared.config.get("feature.essay_detector.chance", 0.30)
                    if message.content and len(message.content) > essay_thresh and random.random() < essay_chance:
                        await message.reply(random.choice(essay_responses), mention_author=False)
                        troll_fired = True
                        try:
                            await shared.logger.log_troll("essay_detector", "Essay Detector", target_user=message.author, channel=message.channel, details={"length": len(message.content)})
                            await shared.logger.increment_stat("essay_detections")
                        except Exception:
                            pass

                # K energy (short dismissive messages)
                if not troll_fired and shared.config.get("feature.k_energy.enabled", True) and message.content and message.content.strip().lower() in ("k", "ok", "okay", "kk"):
                    k_chance = shared.config.get("feature.k_energy.chance", 0.30)
                    if random.random() < k_chance:
                        await message.reply(random.choice(k_responses), mention_author=False)
                        troll_fired = True
                        try:
                            await shared.logger.log_troll("k_energy", "K Energy", target_user=message.author, channel=message.channel)
                            await shared.logger.increment_stat("k_energy_fires")
                        except Exception:
                            pass

                if not troll_fired:
                    # Standard trolls
                    if shared.config.get("feature.per_message_trolls.enabled", True):
                        day = datetime.now(shared.EAT).weekday()
                        troll_chance = shared.config.get("feature.per_message_trolls.weekend_chance", 0.08) if day in (4, 5, 6) else shared.config.get("feature.per_message_trolls.weekday_chance", 0.05)

                        if random.random() < troll_chance:
                            troll_type = random.randint(1, 13)

                            if troll_type == 1:
                                await message.add_reaction("\U0001f1f1")  # Random L

                            elif troll_type == 2:
                                await message.add_reaction("\U0001f480")  # Skull react

                            elif troll_type == 3:
                                combo = random.choice(cursed_emojis)  # Emoji roulette
                                for emoji in combo:
                                    await message.add_reaction(emoji)

                            elif troll_type == 4:
                                # Slow clap
                                clap_emojis = ["\U0001f44f", "\U0001f44f\U0001f3fb", "\U0001f44f\U0001f3fc", "\U0001f44f\U0001f3fd", "\U0001f44f\U0001f3fe", "\U0001f44f\U0001f3ff"]
                                count = random.randint(3, 5)
                                for emoji in clap_emojis[:count]:
                                    await message.add_reaction(emoji)
                                    await asyncio.sleep(2)

                            elif troll_type == 5:
                                # Fake typing
                                async with message.channel.typing():
                                    await asyncio.sleep(random.randint(3, 8))
                                reply = random.choice(fake_typing_messages)
                                if reply:
                                    await message.channel.send(reply)

                            elif troll_type == 6:
                                await message.reply("?", mention_author=False)

                            elif troll_type == 7:
                                await message.reply("nobody asked", mention_author=False)

                            elif troll_type == 8:
                                await message.add_reaction("\U0001f9e2")  # Cap

                            elif troll_type == 9:
                                await message.add_reaction("\U0001f4ee")  # Sus

                            elif troll_type == 10:
                                await message.add_reaction("\U0001f44e")  # Disagree

                            elif troll_type == 11:
                                await message.add_reaction("\U0001f440")  # Read receipt

                            elif troll_type == 12:
                                # Countdown -- 3, 2, 1... nothing
                                for emoji in ["3\ufe0f\u20e3", "2\ufe0f\u20e3", "1\ufe0f\u20e3"]:
                                    await message.add_reaction(emoji)
                                    await asyncio.sleep(2)

                            elif troll_type == 13:
                                await message.reply(random.choice(take_judgements), mention_author=False)  # L/W take

                            try:
                                troll_names = {
                                    1: "Random L", 2: "Skull React", 3: "Emoji Roulette", 4: "Slow Clap",
                                    5: "Fake Typing", 6: "Question Mark", 7: "Nobody Asked", 8: "Cap React",
                                    9: "Sus React", 10: "Disagree React", 11: "Read Receipt", 12: "Countdown",
                                    13: "Take Judgement",
                                }
                                await shared.logger.log_troll(f"msg_troll_{troll_type}", troll_names.get(troll_type, f"Type {troll_type}"), target_user=message.author, channel=message.channel)
                                await shared.logger.increment_stat("per_message_trolls")
                            except Exception:
                                pass

                # Late night bonus trolls
                if shared.config.get("feature.late_night.enabled", True) and is_late_night():
                    bonus_chance = shared.config.get("feature.late_night.bonus_chance", 0.03)
                    if random.random() < bonus_chance:
                        await message.channel.send(random.choice(late_night_messages))
                        try:
                            await shared.logger.log_troll("late_night_bonus", "Late Night Bonus", channel=message.channel)
                            await shared.logger.increment_stat("late_night_bonuses")
                        except Exception:
                            pass

        except Exception:
            pass  # Never let troll errors break command processing


async def setup(bot):
    await bot.add_cog(OnMessage(bot))
