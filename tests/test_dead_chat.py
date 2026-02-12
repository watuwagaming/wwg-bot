"""Tests for cogs/dead_chat.py — dead chat reviver."""

import random
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import bot as shared
from tests.conftest import (
    run_async,
    make_mock_config, make_mock_logger, make_mock_bot,
    make_mock_guild, make_mock_channel,
)

def make_dead_chat_cog(bot):
    from cogs.dead_chat import DeadChat
    cog = object.__new__(DeadChat)
    cog.bot = bot
    cog.last_message_time = None
    return cog

@pytest.fixture
def setup_cog(mock_config, mock_logger, mock_bot):
    channel = make_mock_channel(channel_id=100)
    mock_bot.get_channel = MagicMock(return_value=channel)
    guild = make_mock_guild()
    mock_bot.guilds = [guild]
    cog = make_dead_chat_cog(mock_bot)
    return cog, channel

class TestDeadChatLoop:

    def test_does_nothing_when_disabled(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            shared.config = make_mock_config({"feature.dead_chat.enabled": False})
            await cog.dead_chat_loop()
            channel.send.assert_not_called()
        run_async(_test())

    def test_does_nothing_when_no_guilds(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            cog.bot.guilds = []
            await cog.dead_chat_loop()
            channel.send.assert_not_called()
        run_async(_test())

    def test_does_nothing_when_no_last_message(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            cog.last_message_time = None
            await cog.dead_chat_loop()
            channel.send.assert_not_called()
        run_async(_test())

    def test_does_nothing_when_recent_activity(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            cog.last_message_time = datetime.now(shared.EAT) - timedelta(minutes=30)
            await cog.dead_chat_loop()
            channel.send.assert_not_called()
        run_async(_test())

    def test_sends_when_silence_exceeds_threshold(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            cog.last_message_time = datetime.now(shared.EAT) - timedelta(hours=3)

            with patch("cogs.dead_chat.random") as mock_rand:
                mock_rand.random.return_value = 0.0  # always trigger
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.dead_chat_loop()

            channel.send.assert_called_once()
        run_async(_test())

    def test_resets_last_message_time_after_send(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            old_time = datetime.now(shared.EAT) - timedelta(hours=3)
            cog.last_message_time = old_time

            with patch("cogs.dead_chat.random") as mock_rand:
                mock_rand.random.return_value = 0.0
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.dead_chat_loop()

            assert cog.last_message_time > old_time
        run_async(_test())

    def test_uses_late_night_messages_at_night(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            cog.last_message_time = datetime.now(shared.EAT) - timedelta(hours=3)

            with patch("cogs.dead_chat.random") as mock_rand:
                mock_rand.random.return_value = 0.0
                mock_rand.choice.side_effect = lambda x: x[0]
                with patch("cogs.dead_chat.is_late_night", return_value=True):
                    await cog.dead_chat_loop()

            channel.send.assert_called_once()
            # Late night messages come from late_night_messages list
            from messages import late_night_messages
            assert channel.send.call_args[0][0] == late_night_messages[0]
        run_async(_test())

    def test_uses_hot_takes_during_day(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            cog.last_message_time = datetime.now(shared.EAT) - timedelta(hours=3)

            with patch("cogs.dead_chat.random") as mock_rand:
                mock_rand.random.return_value = 0.0
                mock_rand.choice.side_effect = lambda x: x[0]
                with patch("cogs.dead_chat.is_late_night", return_value=False):
                    await cog.dead_chat_loop()

            from messages import hot_takes
            assert channel.send.call_args[0][0] == hot_takes[0]
        run_async(_test())

    def test_chance_gate_can_prevent_send(self, setup_cog):
        async def _test():
            cog, channel = setup_cog
            cog.last_message_time = datetime.now(shared.EAT) - timedelta(hours=3)

            with patch("cogs.dead_chat.random") as mock_rand:
                mock_rand.random.return_value = 1.0  # never trigger
                await cog.dead_chat_loop()

            channel.send.assert_not_called()
        run_async(_test())
