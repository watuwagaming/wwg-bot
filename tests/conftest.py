"""Shared test fixtures — mocks for discord objects and bot shared state.

IMPORTANT: This file injects mock `discord` and `bot` modules into sys.modules
BEFORE any test or cog file is imported, because importing the real discord.py
hangs in certain sandbox/CI environments.
"""

import asyncio
import enum
import sys
import os
from collections import deque
from datetime import datetime, timedelta
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytz
import pytest


# ============================================================================
# 1. Mock the entire `discord` library BEFORE anything else imports it.
# ============================================================================

class _ActivityType(enum.Enum):
    playing = 0
    streaming = 1
    listening = 2
    watching = 3
    competing = 5

class _Status(enum.Enum):
    online = "online"
    offline = "offline"
    idle = "idle"
    dnd = "dnd"
    invisible = "invisible"

class _DMChannel:
    """Fake DMChannel so isinstance / MagicMock(spec=...) works."""
    pass

class _Member:
    """Fake Member so isinstance checks work."""
    pass

class _Embed:
    """Fake Embed that stores fields."""
    def __init__(self, title=None, description=None, color=None, **kw):
        self.title = title
        self.description = description
        self.color = color
        self.footer = MagicMock()
        self._fields = []
    def add_field(self, name="", value="", inline=True):
        self._fields.append({"name": name, "value": value, "inline": inline})
        return self
    def set_footer(self, text="", icon_url=""):
        self.footer.text = text
        return self
    def set_author(self, name="", icon_url=""):
        return self
    def set_thumbnail(self, url=""):
        return self

class _Color:
    @staticmethod
    def blue():
        return 0x3498db
    @staticmethod
    def red():
        return 0xe74c3c
    @staticmethod
    def green():
        return 0x2ecc71

class _Game:
    def __init__(self, name=""):
        self.name = name
        self.type = _ActivityType.playing

class _Streaming:
    def __init__(self, name="", url=""):
        self.name = name
        self.url = url
        self.type = _ActivityType.streaming

class _Activity:
    def __init__(self, type=None, name=""):
        self.type = type
        self.name = name

class _Intents:
    @classmethod
    def all(cls):
        return cls()
    @classmethod
    def default(cls):
        return cls()

# Exceptions
class _DiscordException(Exception):
    pass

class _HTTPException(_DiscordException):
    def __init__(self, response=None, message=None):
        super().__init__(message or "HTTP error")

class _Forbidden(_HTTPException):
    pass

class _NotFound(_HTTPException):
    pass


# --- discord.ext.commands mock ---

class _CogMeta(type):
    """Metaclass for Cog that stores listeners/commands."""
    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace)
        return cls

class _Cog(metaclass=_CogMeta):
    """Minimal commands.Cog replacement."""
    @classmethod
    def listener(cls, name=None):
        """Decorator that marks a method as an event listener."""
        def decorator(func):
            func.__cog_listener__ = True
            func.__cog_listener_names__ = [name or func.__name__]
            return func
        return decorator

    async def cog_unload(self):
        pass

class _Bot:
    """Minimal commands.Bot stand-in (never instantiated in tests)."""
    def __init__(self, *args, **kwargs):
        pass

def _command(*args, **kwargs):
    """Decorator stub for @commands.command()."""
    def decorator(func):
        return func
    if args and callable(args[0]):
        return args[0]
    return decorator


# --- discord.ext.tasks mock ---

def _loop(**kwargs):
    """Decorator stub for @tasks.loop(). Wraps the function so .start/.cancel work."""
    def decorator(func):
        func.start = MagicMock()
        func.cancel = MagicMock()
        func.stop = MagicMock()
        func.is_running = MagicMock(return_value=False)
        func.before_loop = lambda f: f  # @task.before_loop decorator
        func.after_loop = lambda f: f
        return func
    return decorator


# --- Build and inject fake discord module tree ---

discord_mod = ModuleType("discord")
discord_mod.ActivityType = _ActivityType
discord_mod.Status = _Status
discord_mod.DMChannel = _DMChannel
discord_mod.Member = _Member
discord_mod.Embed = _Embed
discord_mod.Color = _Color
discord_mod.Colour = _Color  # alias
discord_mod.Game = _Game
discord_mod.Streaming = _Streaming
discord_mod.Activity = _Activity
discord_mod.Intents = _Intents
discord_mod.DiscordException = _DiscordException
discord_mod.HTTPException = _HTTPException
discord_mod.Forbidden = _Forbidden
discord_mod.NotFound = _NotFound

# discord.ext
ext_mod = ModuleType("discord.ext")
discord_mod.ext = ext_mod

# discord.ext.commands
commands_mod = ModuleType("discord.ext.commands")
commands_mod.Cog = _Cog
commands_mod.Bot = _Bot
commands_mod.command = _command
ext_mod.commands = commands_mod

# discord.ext.tasks
tasks_mod = ModuleType("discord.ext.tasks")
tasks_mod.loop = _loop
ext_mod.tasks = tasks_mod

sys.modules["discord"] = discord_mod
sys.modules["discord.ext"] = ext_mod
sys.modules["discord.ext.commands"] = commands_mod
sys.modules["discord.ext.tasks"] = tasks_mod


# ============================================================================
# 2. Mock `bot` module (shared state)
# ============================================================================

EAT = pytz.timezone("Africa/Nairobi")

mock_bot_module = ModuleType("bot")
mock_bot_module.EAT = EAT
mock_bot_module.config = None
mock_bot_module.logger = None
mock_bot_module.client = None
sys.modules["bot"] = mock_bot_module

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================================
# 3. Helper to run async tests synchronously
# ============================================================================

def run_async(coro):
    """Run an async coroutine synchronously. Use in place of pytest-asyncio."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ============================================================================
# 4. Reusable mock factories
# ============================================================================

def make_mock_config(overrides=None):
    """Return a MagicMock that mimics BotConfig.get()."""
    from config import DEFAULT_SETTINGS
    defaults = {key: value for key, value, *_ in DEFAULT_SETTINGS}
    if overrides:
        defaults.update(overrides)

    cfg = MagicMock()
    cfg.get = MagicMock(side_effect=lambda key, default=None: defaults.get(key, default))
    return cfg


def make_mock_logger():
    """Return an AsyncMock that mimics BotLogger."""
    logger = AsyncMock()
    logger.log_troll = AsyncMock()
    logger.log_activity = AsyncMock()
    logger.increment_stat = AsyncMock()
    logger.count_message = AsyncMock()
    return logger


def make_mock_channel(channel_id=100, name="general"):
    ch = AsyncMock()
    ch.id = channel_id
    ch.name = name
    ch.guild = MagicMock()
    ch.send = AsyncMock()
    ch.typing = MagicMock(return_value=AsyncMock())
    return ch


def make_mock_member(user_id=1, name="TestUser", bot=False, status=None):
    m = MagicMock()
    m.id = user_id
    m.bot = bot
    m.display_name = name
    m.mention = f"<@{user_id}>"
    m.nick = None
    m.status = status or _Status.online
    m.activities = []
    m.edit = AsyncMock()
    m.send = AsyncMock()
    m.display_avatar = MagicMock()
    m.display_avatar.url = "https://cdn.discordapp.com/avatars/test.png"
    return m


def make_mock_message(content="hello", author=None, channel=None, guild=True):
    msg = AsyncMock()
    msg.content = content
    msg.author = author or make_mock_member()
    msg.channel = channel or make_mock_channel()
    msg.guild = MagicMock() if guild else None
    msg.reference = None
    msg.attachments = []
    msg.created_at = datetime.now()
    msg.add_reaction = AsyncMock()
    msg.reply = AsyncMock()

    # Make isinstance checks work for DMChannel
    if not guild:
        msg.channel = MagicMock(spec=_DMChannel)
        msg.channel.id = 999
        msg.channel.send = AsyncMock()

    return msg


def make_mock_bot(guild=None):
    """Return a MagicMock mimicking commands.Bot."""
    bot = MagicMock()
    bot.user = make_mock_member(user_id=0, name="Bot", bot=True)
    bot.guilds = [guild] if guild else []
    bot.get_channel = MagicMock(return_value=None)
    bot.get_cog = MagicMock(return_value=None)
    bot.get_user = MagicMock(return_value=None)
    bot.fetch_user = AsyncMock(return_value=None)
    bot.change_presence = AsyncMock()
    bot.wait_until_ready = AsyncMock()
    return bot


def make_mock_guild(members=None, channels=None):
    g = MagicMock()
    g.members = members or []
    g.text_channels = channels or []
    g.get_member = MagicMock(side_effect=lambda uid: next((m for m in g.members if m.id == uid), None))
    return g


# ============================================================================
# 5. Pytest fixtures
# ============================================================================

@pytest.fixture
def mock_config():
    """Provides a mock config and patches shared.config."""
    cfg = make_mock_config()
    mock_bot_module.config = cfg
    yield cfg
    mock_bot_module.config = None


@pytest.fixture
def mock_logger():
    """Provides a mock logger and patches shared.logger."""
    lgr = make_mock_logger()
    mock_bot_module.logger = lgr
    yield lgr
    mock_bot_module.logger = None


@pytest.fixture
def mock_bot():
    guild = make_mock_guild()
    bot = make_mock_bot(guild=guild)
    mock_bot_module.client = bot
    yield bot
    mock_bot_module.client = None


@pytest.fixture
def mock_channel():
    return make_mock_channel()


@pytest.fixture
def mock_guild():
    return make_mock_guild()
