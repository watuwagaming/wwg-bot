"""Tests for cogs/modmail.py — DM forwarding and staff reply."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import discord
import pytest

import bot as shared
from tests.conftest import (
    run_async,
    make_mock_config, make_mock_logger, make_mock_bot,
    make_mock_member, make_mock_channel,
)

def make_modmail_cog(bot):
    from cogs.modmail import Modmail
    cog = object.__new__(Modmail)
    cog.bot = bot
    return cog

@pytest.fixture
def setup_cog(mock_config, mock_logger, mock_bot):
    modmail_ch = make_mock_channel(channel_id=1092088239600451584, name="modmail")
    mock_bot.get_channel = MagicMock(return_value=modmail_ch)
    cog = make_modmail_cog(mock_bot)
    return cog, modmail_ch

# ---------------------------------------------------------------------------
# DM Forwarding
# ---------------------------------------------------------------------------

class TestDMForwarding:

    def test_dm_forwarded_to_staff_channel(self, setup_cog):
        async def _test():
            cog, modmail_ch = setup_cog
            author = make_mock_member(user_id=42, name="Gamer")

            # Build DM message
            msg = AsyncMock()
            msg.author = author
            msg.content = "I have a problem"
            msg.channel = MagicMock(spec=discord.DMChannel)
            msg.channel.send = AsyncMock()
            msg.attachments = []
            msg.created_at = datetime.now()

            await cog.on_message(msg)

            # Forwarded embed to modmail channel
            modmail_ch.send.assert_called()
            # Confirmation sent back to user
            msg.channel.send.assert_called_once()
        run_async(_test())

    def test_dm_with_attachments(self, setup_cog):
        async def _test():
            cog, modmail_ch = setup_cog
            author = make_mock_member(user_id=42)

            msg = AsyncMock()
            msg.author = author
            msg.content = "check this"
            msg.channel = MagicMock(spec=discord.DMChannel)
            msg.channel.send = AsyncMock()
            msg.created_at = datetime.now()

            attachment = MagicMock()
            attachment.url = "https://cdn.example.com/image.png"
            msg.attachments = [attachment]

            await cog.on_message(msg)

            # embed + attachment url = 2 sends to modmail channel
            assert modmail_ch.send.call_count == 2
        run_async(_test())

    def test_dm_ignored_when_no_modmail_channel(self, setup_cog):
        async def _test():
            cog, _ = setup_cog
            cog.bot.get_channel = MagicMock(return_value=None)
            # Patch get_channel_by_key to return None
            with patch("cogs.modmail.get_channel_by_key", return_value=None):
                author = make_mock_member(user_id=42)
                msg = AsyncMock()
                msg.author = author
                msg.content = "hello"
                msg.channel = MagicMock(spec=discord.DMChannel)
                msg.channel.send = AsyncMock()
                msg.attachments = []
                msg.created_at = datetime.now()

                await cog.on_message(msg)
                msg.channel.send.assert_not_called()
        run_async(_test())

# ---------------------------------------------------------------------------
# Staff Reply
# ---------------------------------------------------------------------------

class TestStaffReply:
    def test_staff_reply_sends_dm(self, setup_cog):
        async def _test():
            cog, modmail_ch = setup_cog

            target_user = make_mock_member(user_id=42)
            cog.bot.get_user = MagicMock(return_value=target_user)

            # Build the referenced embed message
            embed = MagicMock()
            embed.footer = MagicMock()
            embed.footer.text = "User ID: 42"

            ref_msg = AsyncMock()
            ref_msg.embeds = [embed]

            modmail_ch.fetch_message = AsyncMock(return_value=ref_msg)

            # Build the staff reply
            msg = AsyncMock()
            msg.author = make_mock_member(user_id=99, name="Staff")
            msg.content = "We're looking into it"
            msg.channel = modmail_ch
            msg.reference = MagicMock()
            msg.reference.message_id = 123
            msg.attachments = []
            msg.add_reaction = AsyncMock()

            await cog.on_message(msg)

            target_user.send.assert_called_once_with("We're looking into it")
            msg.add_reaction.assert_called_once_with("\u2705")
        run_async(_test())

    def test_staff_reply_skips_non_embed(self, setup_cog):
        async def _test():
            cog, modmail_ch = setup_cog

            ref_msg = AsyncMock()
            ref_msg.embeds = []

            modmail_ch.fetch_message = AsyncMock(return_value=ref_msg)

            msg = AsyncMock()
            msg.author = make_mock_member(user_id=99)
            msg.content = "reply"
            msg.channel = modmail_ch
            msg.reference = MagicMock()
            msg.reference.message_id = 123
            msg.attachments = []
            msg.add_reaction = AsyncMock()

            await cog.on_message(msg)
            msg.add_reaction.assert_not_called()
        run_async(_test())

# ---------------------------------------------------------------------------
# Skip conditions
# ---------------------------------------------------------------------------

class TestModmailSkips:
    def test_ignores_bot_messages(self, setup_cog):
        async def _test():
            cog, modmail_ch = setup_cog
            msg = AsyncMock()
            msg.author = cog.bot.user
            msg.channel = MagicMock(spec=discord.DMChannel)
            msg.channel.send = AsyncMock()
            await cog.on_message(msg)
            msg.channel.send.assert_not_called()
        run_async(_test())
