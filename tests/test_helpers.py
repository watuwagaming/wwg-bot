"""Tests for helpers.py — utility functions."""

from unittest.mock import MagicMock, patch
from datetime import datetime

import discord
import pytz
import pytest

import bot as shared
from helpers import (
    get_excluded_channels,
    get_troll_channels,
    get_online_members,
    is_late_night,
    get_channel_by_key,
)
from tests.conftest import make_mock_config, make_mock_channel, make_mock_member, make_mock_guild


class TestGetExcludedChannels:
    def test_returns_set(self, mock_config):
        result = get_excluded_channels()
        assert isinstance(result, set)

    def test_contains_configured_ids(self, mock_config):
        result = get_excluded_channels()
        # Default config has a big list of excluded IDs
        assert len(result) > 0

    def test_empty_when_no_exclusions(self):
        shared.config = make_mock_config({"channels.excluded": []})
        result = get_excluded_channels()
        assert result == set()


class TestGetTrollChannels:
    def test_excludes_excluded_channels(self, mock_config):
        excluded_ch = make_mock_channel(channel_id=787194174549393428)
        normal_ch = make_mock_channel(channel_id=12345)
        guild = make_mock_guild(channels=[excluded_ch, normal_ch])
        result = get_troll_channels(guild)
        assert normal_ch in result
        assert excluded_ch not in result

    def test_returns_all_when_no_exclusions(self):
        shared.config = make_mock_config({"channels.excluded": []})
        ch1 = make_mock_channel(channel_id=1)
        ch2 = make_mock_channel(channel_id=2)
        guild = make_mock_guild(channels=[ch1, ch2])
        result = get_troll_channels(guild)
        assert len(result) == 2


class TestGetOnlineMembers:
    def test_excludes_bots(self):
        human = make_mock_member(user_id=1, bot=False, status=discord.Status.online)
        bot_user = make_mock_member(user_id=2, bot=True, status=discord.Status.online)
        guild = make_mock_guild(members=[human, bot_user])
        result = get_online_members(guild)
        assert human in result
        assert bot_user not in result

    def test_excludes_offline(self):
        online = make_mock_member(user_id=1, status=discord.Status.online)
        offline = make_mock_member(user_id=2, status=discord.Status.offline)
        guild = make_mock_guild(members=[online, offline])
        result = get_online_members(guild)
        assert online in result
        assert offline not in result

    def test_includes_idle_and_dnd(self):
        idle = make_mock_member(user_id=1, status=discord.Status.idle)
        dnd = make_mock_member(user_id=2, status=discord.Status.dnd)
        guild = make_mock_guild(members=[idle, dnd])
        result = get_online_members(guild)
        assert len(result) == 2


class TestIsLateNight:
    def test_midnight_is_late(self, mock_config):
        with patch("helpers.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 2, 0, tzinfo=shared.EAT)
            assert is_late_night() is True

    def test_noon_is_not_late(self, mock_config):
        with patch("helpers.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 12, 0, tzinfo=shared.EAT)
            assert is_late_night() is False

    def test_boundary_5am_not_late(self, mock_config):
        with patch("helpers.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2025, 1, 1, 5, 0, tzinfo=shared.EAT)
            assert is_late_night() is False


class TestGetChannelByKey:
    def test_returns_channel_when_configured(self, mock_config, mock_bot):
        ch = make_mock_channel(channel_id=100)
        mock_bot.get_channel = MagicMock(return_value=ch)
        result = get_channel_by_key("channels.general_id")
        assert result == ch

    def test_returns_none_when_not_configured(self, mock_bot):
        shared.config = make_mock_config({"channels.general_id": None})
        # config.get returns None for the key
        shared.config.get = MagicMock(return_value=None)
        result = get_channel_by_key("channels.general_id")
        assert result is None
