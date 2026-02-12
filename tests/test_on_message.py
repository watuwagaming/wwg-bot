"""Tests for cogs/on_message.py — GN police, keyword detectors, trolls."""

import random
from collections import deque
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

import bot as shared
from tests.conftest import (
    run_async,
    make_mock_config, make_mock_logger, make_mock_bot, make_mock_guild,
    make_mock_member, make_mock_message, make_mock_channel,
)

def make_on_message_cog(bot):
    """Construct OnMessage cog without triggering discord.py internals."""
    from cogs.on_message import OnMessage
    cog = object.__new__(OnMessage)
    cog.bot = bot
    cog.gn_watchlist = {}
    cog.recent_message_times = deque(maxlen=200)
    cog.hype_cooldown_until = None
    return cog

@pytest.fixture
def setup_cog(mock_config, mock_logger, mock_bot):
    """Provide a fully-wired OnMessage cog."""
    channel = make_mock_channel(channel_id=100)
    mock_bot.get_channel = MagicMock(return_value=channel)

    cog = make_on_message_cog(mock_bot)
    return cog, channel

# ---------------------------------------------------------------------------
# GN Police
# ---------------------------------------------------------------------------

class TestGNPoliceDetection:
    """Saying 'gn' adds user to the watchlist."""


    def test_gn_adds_to_watchlist(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="gn", channel=channel)
            await cog.on_message(msg)
            assert msg.author.id in cog.gn_watchlist
        run_async(_test())

    def test_goodnight_adds_to_watchlist(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="goodnight everyone", channel=channel)
            await cog.on_message(msg)
            assert msg.author.id in cog.gn_watchlist
        run_async(_test())

    def test_non_gn_ignored(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="hello world", channel=channel)
            await cog.on_message(msg)
            assert msg.author.id not in cog.gn_watchlist
        run_async(_test())

class TestGNPoliceCallout:
    """If a user said gn 20+ mins ago and posts again, they get called out."""

    def test_callout_after_min_minutes(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            author = make_mock_member(user_id=42)
            # Fake that they said gn 30 min ago
            cog.gn_watchlist[42] = datetime.now(shared.EAT) - timedelta(minutes=30)

            msg = make_mock_message(content="actually nvm", author=author, channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0  # always trigger
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            channel.send.assert_called()
            assert 42 not in cog.gn_watchlist  # removed after callout
        run_async(_test())

    def test_no_callout_if_too_soon(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            author = make_mock_member(user_id=42)
            cog.gn_watchlist[42] = datetime.now(shared.EAT) - timedelta(minutes=5)

            msg = make_mock_message(content="back", author=author, channel=channel)
            await cog.on_message(msg)
            # Still in watchlist — no callout yet
            assert 42 in cog.gn_watchlist
        run_async(_test())

    def test_expired_watchlist_entry_removed(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            author = make_mock_member(user_id=42)
            cog.gn_watchlist[42] = datetime.now(shared.EAT) - timedelta(minutes=200)

            msg = make_mock_message(content="I'm back", author=author, channel=channel)
            await cog.on_message(msg)
            assert 42 not in cog.gn_watchlist
        run_async(_test())

# ---------------------------------------------------------------------------
# Keyword Detectors
# ---------------------------------------------------------------------------

class TestRageDetector:
    def test_caps_rage_triggers(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="THIS GAME IS SO BROKEN!!!", channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            msg.reply.assert_called_once()
        run_async(_test())

    def test_short_caps_ignored(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="NO", channel=channel)
            await cog.on_message(msg)
            msg.reply.assert_not_called()
        run_async(_test())

class TestExcuseGenerator:
    def test_loss_phrase_triggers(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="we lost so bad", channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            msg.reply.assert_called_once()
        run_async(_test())

class TestCapAlarm:
    def test_no_cap_triggers(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            # Disable rage and excuse so cap can fire
            shared.config = make_mock_config({
                "feature.rage_detector.enabled": False,
                "feature.excuse_generator.enabled": False,
            })
            msg = make_mock_message(content="no cap bro", channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            msg.reply.assert_called_once()
        run_async(_test())

class TestFlexPolice:
    def test_flex_triggers(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            shared.config = make_mock_config({
                "feature.rage_detector.enabled": False,
                "feature.excuse_generator.enabled": False,
                "feature.cap_alarm.enabled": False,
            })
            msg = make_mock_message(content="im the best at this game", channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            msg.reply.assert_called_once()
        run_async(_test())

class TestLagDefender:
    def test_lag_triggers(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            shared.config = make_mock_config({
                "feature.rage_detector.enabled": False,
                "feature.excuse_generator.enabled": False,
                "feature.cap_alarm.enabled": False,
                "feature.flex_police.enabled": False,
            })
            msg = make_mock_message(content="it was lag", channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            msg.reply.assert_called_once()
        run_async(_test())

# ---------------------------------------------------------------------------
# Essay / K
# ---------------------------------------------------------------------------

class TestEssayDetector:
    def test_long_message_triggers(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="a" * 600, channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            msg.reply.assert_called()
        run_async(_test())

class TestKEnergy:
    def test_k_triggers(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="k", channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            msg.reply.assert_called()
        run_async(_test())

# ---------------------------------------------------------------------------
# Skip conditions
# ---------------------------------------------------------------------------

class TestOnMessageSkips:
    def test_ignores_bot_messages(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="gn", channel=channel)
            msg.author = cog.bot.user
            await cog.on_message(msg)
            assert len(cog.gn_watchlist) == 0
        run_async(_test())

    def test_ignores_dms(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            msg = make_mock_message(content="gn", guild=False)
            await cog.on_message(msg)
            assert len(cog.gn_watchlist) == 0
        run_async(_test())

    def test_ignores_excluded_channel(self, setup_cog):
        async def _test():
            cog, _ = setup_cog
            # Use an excluded channel ID
            excluded_ch = make_mock_channel(channel_id=787194174549393428)
            excluded_ch.guild = MagicMock()
            msg = make_mock_message(content="THIS IS SO BROKEN!!!", channel=excluded_ch)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            msg.reply.assert_not_called()
        run_async(_test())

# ---------------------------------------------------------------------------
# Cross-cog wiring
# ---------------------------------------------------------------------------

class TestCrossCogWiring:
    def test_updates_dead_chat_timestamp(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            dead_chat_cog = MagicMock()
            dead_chat_cog.last_message_time = None
            cog.bot.get_cog = MagicMock(side_effect=lambda name: dead_chat_cog if name == "DeadChat" else None)

            msg = make_mock_message(content="hello", channel=channel)
            await cog.on_message(msg)
            assert dead_chat_cog.last_message_time is not None
        run_async(_test())

    def test_caches_message_for_this_you(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            bg_cog = MagicMock()
            bg_cog.message_cache = deque(maxlen=50)
            cog.bot.get_cog = MagicMock(side_effect=lambda name: bg_cog if name == "BackgroundTrolls" else None)

            msg = make_mock_message(content="this is a long enough message to cache", channel=channel)

            with patch("cogs.on_message.random") as mock_random:
                mock_random.random.return_value = 0.0  # always cache
                mock_random.choice.side_effect = lambda x: x[0]
                await cog.on_message(msg)

            assert len(bg_cog.message_cache) == 1
        run_async(_test())
