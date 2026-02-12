"""Tests for cogs/background_trolls.py — individual troll functions."""

from collections import deque
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

import bot as shared
from tests.conftest import (
    run_async,
    make_mock_config, make_mock_logger, make_mock_bot, make_mock_guild,
    make_mock_member, make_mock_channel,
)

def make_bg_trolls_cog(bot):
    from cogs.background_trolls import BackgroundTrolls
    cog = object.__new__(BackgroundTrolls)
    cog.bot = bot
    cog.message_cache = deque(maxlen=50)
    return cog

@pytest.fixture
def setup_cog(mock_config, mock_logger, mock_bot):
    channel = make_mock_channel(channel_id=100)
    mock_bot.get_channel = MagicMock(return_value=channel)

    member1 = make_mock_member(user_id=1, name="Alice")
    member2 = make_mock_member(user_id=2, name="Bob")
    guild = make_mock_guild(members=[member1, member2])
    mock_bot.guilds = [guild]

    cog = make_bg_trolls_cog(mock_bot)
    return cog, guild, channel

class TestJumpscarePing:

    def test_sends_to_channel(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.jumpscare_ping(guild)
            channel.send.assert_called_once()
        run_async(_test())

    def test_no_members_no_send(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.get_online_members", return_value=[]):
                await cog.jumpscare_ping(guild)
            channel.send.assert_not_called()
        run_async(_test())

class TestThisYou:
    def test_quotes_cached_message(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            cog.message_cache.append((1, "I love pineapple on pizza", 100))
            guild.get_member = MagicMock(return_value=make_mock_member(user_id=1))

            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0] if not isinstance(x, deque) else list(x)[0]
                await cog.this_you(guild)

            channel.send.assert_called_once()
            call_text = channel.send.call_args[0][0]
            assert "this you?" in call_text
        run_async(_test())

    def test_empty_cache_no_send(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            await cog.this_you(guild)
            channel.send.assert_not_called()
        run_async(_test())

class TestRenameRoulette:
    def test_renames_member(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                with patch("cogs.background_trolls.asyncio") as mock_asyncio:
                    mock_asyncio.sleep = AsyncMock()
                    await cog.rename_roulette(guild)

            channel.send.assert_called_once()
            # Victim should have been edited twice (rename + revert)
            victim = guild.members[0]
            assert victim.edit.call_count == 2
        run_async(_test())

class TestFakeModAction:
    def test_sends_warning(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.fake_mod_action(guild)
            channel.send.assert_called_once()
            assert "WARNING" in channel.send.call_args[0][0]
        run_async(_test())

class TestServerDrama:
    def test_sends_drama(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                mock_rand.sample.side_effect = lambda pop, k: list(pop)[:k]
                await cog.server_drama(guild)
            channel.send.assert_called_once()
        run_async(_test())

    def test_needs_two_members(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.get_online_members", return_value=[make_mock_member(user_id=1)]):
                await cog.server_drama(guild)
            channel.send.assert_not_called()
        run_async(_test())

class TestAfkCheck:
    def test_pings_member(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.afk_check(guild)
            channel.send.assert_called_once()
        run_async(_test())

class TestRandomPoll:
    def test_sends_poll_and_adds_reactions(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            msg = AsyncMock()
            msg.add_reaction = AsyncMock()
            channel.send = AsyncMock(return_value=msg)

            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.random_poll(guild)

            channel.send.assert_called_once()
            assert msg.add_reaction.call_count >= 2
        run_async(_test())

class TestMotivationalMisquote:
    def test_sends_quote(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.motivational_misquote(guild)
            channel.send.assert_called_once()
            assert "Inspirational Quote" in channel.send.call_args[0][0]
        run_async(_test())

class TestConspiracyTheory:
    def test_sends_theory(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.conspiracy_theory(guild)
            channel.send.assert_called_once()
            assert "THREAD" in channel.send.call_args[0][0]
        run_async(_test())

class TestHypeMan:
    def test_sends_hype(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.random") as mock_rand:
                mock_rand.choice.side_effect = lambda x: x[0]
                await cog.hype_man(guild)
            channel.send.assert_called_once()
        run_async(_test())

class TestFridayHype:
    def test_fires_on_friday(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.datetime") as mock_dt:
                mock_dt.now.return_value = MagicMock(weekday=MagicMock(return_value=4))
                with patch("cogs.background_trolls.random") as mock_rand:
                    mock_rand.choice.side_effect = lambda x: x[0]
                    await cog.friday_hype(guild)
            channel.send.assert_called_once()
        run_async(_test())

    def test_skips_non_friday(self, setup_cog):
        async def _test():
            cog, guild, channel = setup_cog
            with patch("cogs.background_trolls.datetime") as mock_dt:
                mock_dt.now.return_value = MagicMock(weekday=MagicMock(return_value=1))
                await cog.friday_hype(guild)
            channel.send.assert_not_called()
        run_async(_test())

class TestGetBackgroundTrolls:
    def test_returns_14_trolls(self, setup_cog):
        cog, _, _ = setup_cog
        trolls = cog._get_background_trolls()
        assert len(trolls) == 14
        for fn, name in trolls:
            assert callable(fn)
            assert isinstance(name, str)
