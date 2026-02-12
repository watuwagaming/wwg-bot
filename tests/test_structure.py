"""Structural tests — verify imports, cog setup functions, and project layout."""

import asyncio
import importlib
import inspect
import os
import sys

import pytest


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestModuleImports:
    """All modules import without errors."""

    def test_messages_imports(self):
        import messages
        assert messages

    def test_helpers_imports(self):
        import helpers
        assert helpers

    def test_config_imports(self):
        from config import BotConfig, DEFAULT_SETTINGS
        assert BotConfig
        assert len(DEFAULT_SETTINGS) > 0

    def test_database_imports(self):
        from database import init_db, DEFAULT_STATS
        assert init_db
        assert len(DEFAULT_STATS) > 0

    def test_logger_imports(self):
        from logger import BotLogger
        assert BotLogger


class TestCogSetupFunctions:
    """Every cog has an async setup(bot) function."""

    COG_MODULES = [
        "cogs.background_trolls",
        "cogs.dead_chat",
        "cogs.morning_greeting",
        "cogs.status_rotation",
        "cogs.events",
        "cogs.modmail",
        "cogs.on_message",
    ]

    @pytest.mark.parametrize("mod_name", COG_MODULES)
    def test_cog_has_async_setup(self, mod_name):
        mod = importlib.import_module(mod_name)
        assert hasattr(mod, "setup"), f"{mod_name} missing setup()"
        assert asyncio.iscoroutinefunction(mod.setup), f"{mod_name}.setup is not async"


class TestCogClasses:
    """Each cog module has the expected Cog class."""

    def test_background_trolls_class(self):
        from cogs.background_trolls import BackgroundTrolls
        assert BackgroundTrolls

    def test_dead_chat_class(self):
        from cogs.dead_chat import DeadChat
        assert DeadChat

    def test_morning_greeting_class(self):
        from cogs.morning_greeting import MorningGreeting
        assert MorningGreeting

    def test_status_rotation_class(self):
        from cogs.status_rotation import StatusRotation
        assert StatusRotation

    def test_events_class(self):
        from cogs.events import Events
        assert Events

    def test_modmail_class(self):
        from cogs.modmail import Modmail
        assert Modmail

    def test_on_message_class(self):
        from cogs.on_message import OnMessage
        assert OnMessage


class TestMainEntryPoint:
    """main.py has the expected structure."""

    def test_main_py_exists(self):
        assert os.path.isfile(os.path.join(PROJECT_ROOT, "main.py"))

    def test_main_loads_all_cogs(self):
        main_src = open(os.path.join(PROJECT_ROOT, "main.py")).read()
        expected_cogs = [
            "cogs.background_trolls",
            "cogs.dead_chat",
            "cogs.morning_greeting",
            "cogs.status_rotation",
            "cogs.events",
            "cogs.modmail",
            "cogs.on_message",
        ]
        for cog in expected_cogs:
            assert cog in main_src, f"main.py missing cog: {cog}"

    def test_main_has_no_on_message_handler(self):
        main_src = open(os.path.join(PROJECT_ROOT, "main.py")).read()
        assert "async def on_message" not in main_src

    def test_main_initializes_config_before_cogs(self):
        main_src = open(os.path.join(PROJECT_ROOT, "main.py")).read()
        config_pos = main_src.index("BotConfig()")
        cog_pos = main_src.index("load_extension")
        assert config_pos < cog_pos


class TestProjectFileStructure:
    """Expected files exist in the project."""

    EXPECTED_FILES = [
        "main.py",
        "bot.py",
        "messages.py",
        "helpers.py",
        "config.py",
        "database.py",
        "logger.py",
        "cogs/__init__.py",
        "cogs/background_trolls.py",
        "cogs/dead_chat.py",
        "cogs/morning_greeting.py",
        "cogs/status_rotation.py",
        "cogs/events.py",
        "cogs/modmail.py",
        "cogs/on_message.py",
    ]

    @pytest.mark.parametrize("filepath", EXPECTED_FILES)
    def test_file_exists(self, filepath):
        full = os.path.join(PROJECT_ROOT, filepath)
        assert os.path.isfile(full), f"Missing file: {filepath}"


class TestNoCircularImports:
    """Cog modules don't create circular import chains."""

    COG_MODULES = [
        "cogs.background_trolls",
        "cogs.dead_chat",
        "cogs.morning_greeting",
        "cogs.status_rotation",
        "cogs.events",
        "cogs.modmail",
        "cogs.on_message",
    ]

    @pytest.mark.parametrize("mod_name", COG_MODULES)
    def test_no_circular_import(self, mod_name):
        """Each cog can be imported independently without import errors."""
        mod = importlib.import_module(mod_name)
        assert mod is not None
