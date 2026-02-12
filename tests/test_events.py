"""Tests for cogs/events.py — game detection, typing callout, reaction chain, welcome."""

import random
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

import bot as shared
from tests.conftest import (
    run_async,
    make_mock_config, make_mock_logger, make_mock_bot, make_mock_guild,
    make_mock_member, make_mock_channel,
)

def make_events_cog(bot):
    """Construct Events cog without discord.py internals."""
    from cogs.events import Events
    cog = object.__new__(Events)
    cog.bot = bot
    cog.game_notify_cooldown = {}
    cog.game_user_ping_cooldown = {}
    cog.typing_tracker = {}
    return cog

@pytest.fixture
def setup_cog(mock_config, mock_logger, mock_bot):
    channel = make_mock_channel(channel_id=100)
    mock_bot.get_channel = MagicMock(return_value=channel)
    cog = make_events_cog(mock_bot)
    return cog, channel

# ---------------------------------------------------------------------------
# Game Detection
# ---------------------------------------------------------------------------

def make_activity(name, atype=discord.ActivityType.playing):
    a = MagicMock()
    a.type = atype
    a.name = name
    return a

class TestGameDetection:

    def test_skips_bots(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            before = make_mock_member(user_id=1, bot=True)
            after = make_mock_member(user_id=1, bot=True)
            after.activities = [make_activity("Fortnite")]
            await cog.on_presence_update(before, after)
            channel.send.assert_not_called()
        run_async(_test())

    def test_skips_when_disabled(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            shared.config = make_mock_config({"feature.game_detection.enabled": False})
            before = make_mock_member(user_id=1)
            after = make_mock_member(user_id=1)
            after.activities = [make_activity("Fortnite")]
            await cog.on_presence_update(before, after)
            channel.send.assert_not_called()
        run_async(_test())

    def test_skips_no_new_games(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            before = make_mock_member(user_id=1)
            before.activities = [make_activity("Fortnite")]
            after = make_mock_member(user_id=1)
            after.activities = [make_activity("Fortnite")]
            await cog.on_presence_update(before, after)
            channel.send.assert_not_called()
        run_async(_test())

    def test_game_cooldown_blocks_repeat(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            cog.game_notify_cooldown["Fortnite"] = datetime.now(shared.EAT)

            before = make_mock_member(user_id=1)
            before.activities = []
            after = make_mock_member(user_id=1)
            after.activities = [make_activity("Fortnite")]

            # Set up guild with other players
            player2 = make_mock_member(user_id=2)
            player2.activities = [make_activity("Fortnite")]
            player3 = make_mock_member(user_id=3)
            player3.activities = [make_activity("Fortnite")]
            guild = make_mock_guild(members=[after, player2, player3])
            after.guild = guild

            await cog.on_presence_update(before, after)
            channel.send.assert_not_called()
        run_async(_test())

    def test_user_cooldown_blocks_repeat(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            # User pinged recently
            cog.game_user_ping_cooldown[1] = datetime.now(shared.EAT)

            shared.config = make_mock_config({
                "feature.game_detection.chance": 1.0,
                "feature.game_detection.min_players": 2,
            })

            before = make_mock_member(user_id=1)
            before.activities = []
            after = make_mock_member(user_id=1)
            after.activities = [make_activity("Fortnite")]

            player2 = make_mock_member(user_id=2)
            player2.activities = [make_activity("Fortnite")]
            player3 = make_mock_member(user_id=3)
            player3.activities = [make_activity("Fortnite")]
            guild = make_mock_guild(members=[after, player2, player3])
            after.guild = guild

            await cog.on_presence_update(before, after)
            channel.send.assert_not_called()
        run_async(_test())

    def test_fires_when_conditions_met(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            shared.config = make_mock_config({
                "feature.game_detection.chance": 1.0,
                "feature.game_detection.min_players": 2,
                "feature.game_detection.game_cooldown_sec": 86400,
                "feature.game_detection.user_cooldown_sec": 86400,
            })

            before = make_mock_member(user_id=1)
            before.activities = []
            after = make_mock_member(user_id=1)
            after.activities = [make_activity("Fortnite")]

            player2 = make_mock_member(user_id=2)
            player2.activities = [make_activity("Fortnite")]
            player3 = make_mock_member(user_id=3)
            player3.activities = [make_activity("Fortnite")]
            guild = make_mock_guild(members=[after, player2, player3])
            after.guild = guild

            with patch("cogs.events.random") as mock_rand:
                mock_rand.random.return_value = 0.0
                await cog.on_presence_update(before, after)

            channel.send.assert_called_once()
            # Verify cooldowns were set
            assert "Fortnite" in cog.game_notify_cooldown
            assert 1 in cog.game_user_ping_cooldown
        run_async(_test())

# ---------------------------------------------------------------------------
# Typing Callout
# ---------------------------------------------------------------------------

class TestTypingCallout:
    def test_first_typing_event_just_records(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            user = make_mock_member(user_id=5)
            channel.guild = MagicMock()
            await cog.on_typing(channel, user, datetime.now())
            assert (channel.id, user.id) in cog.typing_tracker
            channel.send.assert_not_called()
        run_async(_test())

    def test_callout_after_duration(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            user = make_mock_member(user_id=5)
            channel.guild = MagicMock()

            # Pre-populate tracker as if they started typing 90 seconds ago
            cog.typing_tracker[(channel.id, user.id)] = datetime.now(shared.EAT) - timedelta(seconds=90)

            with patch("cogs.events.random") as mock_rand:
                mock_rand.random.return_value = 0.0
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.on_typing(channel, user, datetime.now())

            channel.send.assert_called_once()
            assert (channel.id, user.id) not in cog.typing_tracker
        run_async(_test())

    def test_stale_entry_removed(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            user = make_mock_member(user_id=5)
            channel.guild = MagicMock()

            cog.typing_tracker[(channel.id, user.id)] = datetime.now(shared.EAT) - timedelta(seconds=200)

            with patch("cogs.events.random") as mock_rand:
                mock_rand.random.return_value = 1.0  # won't trigger callout
                await cog.on_typing(channel, user, datetime.now())

            assert (channel.id, user.id) not in cog.typing_tracker
        run_async(_test())

    def test_skips_bots(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            user = make_mock_member(user_id=5, bot=True)
            await cog.on_typing(channel, user, datetime.now())
            assert (channel.id, user.id) not in cog.typing_tracker
        run_async(_test())

    def test_skips_excluded_channel(self, setup_cog):
        async def _test():
            cog, _ = setup_cog
            excluded = make_mock_channel(channel_id=787194174549393428)
            excluded.guild = MagicMock()
            user = make_mock_member(user_id=5)
            await cog.on_typing(excluded, user, datetime.now())
            assert (excluded.id, user.id) not in cog.typing_tracker
        run_async(_test())

# ---------------------------------------------------------------------------
# Reaction Chain
# ---------------------------------------------------------------------------

class TestReactionChain:
    def test_joins_at_threshold(self, setup_cog):
        async def _test():
            cog, _ = setup_cog

            user = make_mock_member(user_id=5)
            # Create mock reaction with 3 non-bot reactors
            reactors = [make_mock_member(user_id=i) for i in range(10, 13)]

            reaction = MagicMock()
            reaction.users = MagicMock(return_value=AsyncIterator(reactors))
            reaction.message = MagicMock()
            reaction.message.add_reaction = AsyncMock()
            reaction.message.channel = make_mock_channel()
            reaction.emoji = "\U0001f525"

            await cog.on_reaction_add(reaction, user)
            reaction.message.add_reaction.assert_called_once_with("\U0001f525")
        run_async(_test())

    def test_skips_if_bot_already_reacted(self, setup_cog):
        async def _test():
            cog, _ = setup_cog

            user = make_mock_member(user_id=5)
            bot_user = cog.bot.user

            reactors = [bot_user] + [make_mock_member(user_id=i) for i in range(10, 13)]
            reaction = MagicMock()
            reaction.users = MagicMock(return_value=AsyncIterator(reactors))
            reaction.message = MagicMock()
            reaction.message.add_reaction = AsyncMock()

            await cog.on_reaction_add(reaction, user)
            reaction.message.add_reaction.assert_not_called()
        run_async(_test())

    def test_skips_below_threshold(self, setup_cog):
        async def _test():
            cog, _ = setup_cog

            user = make_mock_member(user_id=5)
            reactors = [make_mock_member(user_id=10)]
            reaction = MagicMock()
            reaction.users = MagicMock(return_value=AsyncIterator(reactors))
            reaction.message = MagicMock()
            reaction.message.add_reaction = AsyncMock()

            await cog.on_reaction_add(reaction, user)
            reaction.message.add_reaction.assert_not_called()
        run_async(_test())

    def test_skips_bot_user(self, setup_cog):
        async def _test():
            cog, _ = setup_cog
            user = make_mock_member(user_id=5, bot=True)
            reaction = MagicMock()
            reaction.message = MagicMock()
            reaction.message.add_reaction = AsyncMock()
            await cog.on_reaction_add(reaction, user)
            reaction.message.add_reaction.assert_not_called()
        run_async(_test())

# ---------------------------------------------------------------------------
# Helper: async iterator for mock reaction.users()
# ---------------------------------------------------------------------------

class AsyncIterator:
    """Wraps a list to be used as an async iterator (for reaction.users())."""

    def __init__(self, items):
        self._items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._items)
        except StopIteration:
            raise StopAsyncIteration
