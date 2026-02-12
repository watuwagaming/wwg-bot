"""BotConfig: in-memory config backed by a JSON file."""

import json
import asyncio
from pathlib import Path


# All default settings with metadata for the dashboard
# (key, default_value, value_type, category, description)
DEFAULT_SETTINGS = [
    # Morning Greeting
    ("feature.morning_greeting.enabled", True, "bool", "Morning Greeting", "Enable morning greeting messages"),
    ("feature.morning_greeting.channel_id", "628278524905521179", "string", "Morning Greeting", "Channel for morning greetings"),
    ("feature.morning_greeting.hour_min", 6, "int", "Morning Greeting", "Earliest hour for greeting (EAT)"),
    ("feature.morning_greeting.hour_max", 10, "int", "Morning Greeting", "Latest hour for greeting (EAT)"),

    # Troll Loop
    ("feature.troll_loop.enabled", True, "bool", "Troll Loop", "Enable background troll loop"),
    ("feature.troll_loop.weekday_min_hours", 1.0, "float", "Troll Loop", "Min hours between trolls (weekdays)"),
    ("feature.troll_loop.weekday_max_hours", 4.0, "float", "Troll Loop", "Max hours between trolls (weekdays)"),
    ("feature.troll_loop.weekend_min_hours", 0.5, "float", "Troll Loop", "Min hours between trolls (weekends)"),
    ("feature.troll_loop.weekend_max_hours", 2.0, "float", "Troll Loop", "Max hours between trolls (weekends)"),
    ("feature.troll_loop.initial_delay_min", 300, "int", "Troll Loop", "Min initial delay in seconds"),
    ("feature.troll_loop.initial_delay_max", 1800, "int", "Troll Loop", "Max initial delay in seconds"),

    # Dead Chat Reviver
    ("feature.dead_chat.enabled", True, "bool", "Dead Chat Reviver", "Enable dead chat reviver"),
    ("feature.dead_chat.check_interval_min", 30, "int", "Dead Chat Reviver", "Check interval in minutes"),
    ("feature.dead_chat.silence_threshold_sec", 7200, "int", "Dead Chat Reviver", "Silence threshold in seconds"),
    ("feature.dead_chat.chance", 0.05, "float", "Dead Chat Reviver", "Chance to revive (0-1)"),
    ("feature.dead_chat.channel_id", "750702727566327869", "string", "Dead Chat Reviver", "Channel for dead chat revival"),

    # Status Rotation
    ("feature.status_rotation.enabled", True, "bool", "Status Rotation", "Enable status rotation"),
    ("feature.status_rotation.interval_sec", 600, "int", "Status Rotation", "Interval between rotations in seconds"),
    ("feature.status_rotation.member_mention_chance", 0.10, "float", "Status Rotation", "Chance to show 'Playing with [member]'"),

    # Game Detection
    ("feature.game_detection.enabled", True, "bool", "Game Detection", "Enable game detection pings"),
    ("feature.game_detection.min_players", 2, "int", "Game Detection", "Min players already in-game to trigger"),
    ("feature.game_detection.chance", 0.03, "float", "Game Detection", "Chance to ping (0-1)"),
    ("feature.game_detection.game_cooldown_sec", 86400, "int", "Game Detection", "Per-game cooldown in seconds"),
    ("feature.game_detection.user_cooldown_sec", 86400, "int", "Game Detection", "Per-user cooldown in seconds"),
    ("feature.game_detection.channel_id", "1355493926492180632", "string", "Game Detection", "Channel for game detection"),

    # Typing Callout
    ("feature.typing_callout.enabled", True, "bool", "Typing Callout", "Enable typing callout"),
    ("feature.typing_callout.duration_sec", 60, "int", "Typing Callout", "Seconds of typing before callout"),
    ("feature.typing_callout.chance", 0.10, "float", "Typing Callout", "Chance to call out (0-1)"),
    ("feature.typing_callout.stale_sec", 120, "int", "Typing Callout", "Seconds before tracker entry goes stale"),

    # Reaction Chain
    ("feature.reaction_chain.enabled", True, "bool", "Reaction Chain", "Enable reaction chain joining"),
    ("feature.reaction_chain.threshold", 3, "int", "Reaction Chain", "Min non-bot reactions to trigger"),

    # GN Police
    ("feature.gn_police.enabled", True, "bool", "GN Police", "Enable goodnight police"),
    ("feature.gn_police.min_minutes", 20, "int", "GN Police", "Min minutes after GN to call out"),
    ("feature.gn_police.max_minutes", 180, "int", "GN Police", "Max minutes after GN to call out"),
    ("feature.gn_police.chance", 0.10, "float", "GN Police", "Chance to call out (0-1)"),

    # Hype Detector
    ("feature.hype_detector.enabled", True, "bool", "Hype Detector", "Enable hype detector"),
    ("feature.hype_detector.threshold_messages", 15, "int", "Hype Detector", "Messages in time window to trigger"),
    ("feature.hype_detector.time_window_sec", 60, "int", "Hype Detector", "Time window in seconds"),
    ("feature.hype_detector.cooldown_min", 30, "int", "Hype Detector", "Cooldown in minutes after triggering"),
    ("feature.hype_detector.weekday_chance", 0.05, "float", "Hype Detector", "Chance on weekdays (0-1)"),
    ("feature.hype_detector.weekend_chance", 0.05, "float", "Hype Detector", "Chance on weekends (0-1)"),

    # Late Night Mode
    ("feature.late_night.enabled", True, "bool", "Late Night Mode", "Enable late night bonus trolls"),
    ("feature.late_night.start_hour", 0, "int", "Late Night Mode", "Start hour (EAT)"),
    ("feature.late_night.end_hour", 5, "int", "Late Night Mode", "End hour (EAT)"),
    ("feature.late_night.bonus_chance", 0.03, "float", "Late Night Mode", "Bonus troll chance (0-1)"),

    # Welcome Hazing
    ("feature.welcome_hazing.enabled", True, "bool", "Welcome Hazing", "Enable welcome hazing"),
    ("feature.welcome_hazing.chance", 0.10, "float", "Welcome Hazing", "Chance to haze new member (0-1)"),
    ("feature.welcome_hazing.nick_revert_min_hours", 1.0, "float", "Welcome Hazing", "Min hours before reverting nickname"),
    ("feature.welcome_hazing.nick_revert_max_hours", 168.0, "float", "Welcome Hazing", "Max hours before reverting nickname"),

    # Rage Detector
    ("feature.rage_detector.enabled", True, "bool", "Rage Detector", "Enable rage detector"),
    ("feature.rage_detector.caps_threshold", 0.70, "float", "Rage Detector", "Caps ratio to detect rage (0-1)"),
    ("feature.rage_detector.min_length", 10, "int", "Rage Detector", "Min message length for caps check"),
    ("feature.rage_detector.exclaim_threshold", 3, "int", "Rage Detector", "Exclamation marks to detect rage"),
    ("feature.rage_detector.chance", 0.10, "float", "Rage Detector", "Chance to respond (0-1)"),

    # Excuse Generator
    ("feature.excuse_generator.enabled", True, "bool", "Excuse Generator", "Enable excuse generator"),
    ("feature.excuse_generator.chance", 0.10, "float", "Excuse Generator", "Chance to respond (0-1)"),

    # Cap Alarm
    ("feature.cap_alarm.enabled", True, "bool", "Cap Alarm", "Enable cap alarm"),
    ("feature.cap_alarm.chance", 0.10, "float", "Cap Alarm", "Chance to respond (0-1)"),

    # Flex Police
    ("feature.flex_police.enabled", True, "bool", "Flex Police", "Enable flex police"),
    ("feature.flex_police.chance", 0.10, "float", "Flex Police", "Chance to respond (0-1)"),

    # Lag Defender
    ("feature.lag_defender.enabled", True, "bool", "Lag Defender", "Enable lag defender"),
    ("feature.lag_defender.chance", 0.10, "float", "Lag Defender", "Chance to respond (0-1)"),

    # Essay Detector
    ("feature.essay_detector.enabled", True, "bool", "Essay Detector", "Enable essay detector"),
    ("feature.essay_detector.threshold_chars", 500, "int", "Essay Detector", "Min characters to trigger"),
    ("feature.essay_detector.chance", 0.10, "float", "Essay Detector", "Chance to respond (0-1)"),

    # K Energy
    ("feature.k_energy.enabled", True, "bool", "K Energy", "Enable K energy detector"),
    ("feature.k_energy.chance", 0.10, "float", "K Energy", "Chance to respond (0-1)"),

    # Per-Message Trolls
    ("feature.per_message_trolls.enabled", True, "bool", "Per-Message Trolls", "Enable per-message troll reactions"),
    ("feature.per_message_trolls.weekday_chance", 0.05, "float", "Per-Message Trolls", "Base chance on weekdays (0-1)"),
    ("feature.per_message_trolls.weekend_chance", 0.08, "float", "Per-Message Trolls", "Base chance on weekends (0-1)"),

    # Message Cache
    ("feature.message_cache.chance", 0.10, "float", "Per-Message Trolls", "Chance to cache a message for 'this you'"),

    # Channels
    ("channels.general_id", "750702727566327869", "string", "Channels", "General channel ID"),
    ("channels.greetings_id", "628278524905521179", "string", "Channels", "Greetings channel ID"),
    ("channels.gamers_arena_id", "1355493926492180632", "string", "Channels", "Gamers Arena channel ID"),
    ("channels.modmail_id", "1092088239600451584", "string", "Channels", "Modmail channel ID"),
    ("channels.excluded", [
        787194174549393428, 716572818262720572, 812233686958342145,
        740807136703021157, 1352324423591399505, 628278524905521179,
        1136556546168471602, 745494439455227955, 1238490815580471327,
        1131832842402410618, 1092088239600451584, 1092088977030393977,
        1238489063485603840, 729602427157872752, 1095785282575548466,
        668549913730088970, 1355492254869098736, 1026342989053829170,
        1026343418374397956, 808056824024268807, 1245077589752680550,
        1353367229453828118, 799116876721684542, 628279095490379777,
        1072396997232951376, 1463410054223892543, 658572685273726997,
        1124720930665545918, 726444462057717770, 819785075599474688,
        1062661844680052806, 899175840930205748, 846404140711149598,
        802584507412250674,
    ], "json", "Channels", "Channel IDs excluded from trolling"),

    # Background Trolls (individual toggles)
    ("bg_troll.jumpscare_ping.enabled", True, "bool", "Background Trolls", "Jumpscare Ping"),
    ("bg_troll.this_you.enabled", True, "bool", "Background Trolls", "This You?"),
    ("bg_troll.rename_roulette.enabled", True, "bool", "Background Trolls", "Rename Roulette"),
    ("bg_troll.vibe_check.enabled", True, "bool", "Background Trolls", "Vibe Check"),
    ("bg_troll.wrong_channel.enabled", True, "bool", "Background Trolls", "Wrong Channel"),
    ("bg_troll.fake_mod_action.enabled", True, "bool", "Background Trolls", "Fake Mod Action"),
    ("bg_troll.server_drama.enabled", True, "bool", "Background Trolls", "Server Drama"),
    ("bg_troll.afk_check.enabled", True, "bool", "Background Trolls", "AFK Check"),
    ("bg_troll.random_poll.enabled", True, "bool", "Background Trolls", "Random Poll"),
    ("bg_troll.motivational_misquote.enabled", True, "bool", "Background Trolls", "Motivational Misquote"),
    ("bg_troll.fake_announcement.enabled", True, "bool", "Background Trolls", "Fake Announcement"),
    ("bg_troll.conspiracy_theory.enabled", True, "bool", "Background Trolls", "Conspiracy Theory"),
    ("bg_troll.hype_man.enabled", True, "bool", "Background Trolls", "Hype Man"),
    ("bg_troll.friday_hype.enabled", True, "bool", "Background Trolls", "Friday Hype"),
]

# Build metadata lookup: key -> (value_type, category, description)
_META = {key: (vtype, cat, desc) for key, _, vtype, cat, desc in DEFAULT_SETTINGS}


class BotConfig:
    """
    Read path:  config.get("key") -> value  (dict lookup, zero I/O)
    Write path: config.set("key", val) -> updates dict + writes config.json
    """

    def __init__(self, path: str = "config.json"):
        self._path = Path(path)
        self._data: dict = {}
        self._lock = asyncio.Lock()

    def load(self):
        """Load config from JSON file, merging with defaults for any missing keys."""
        # Start with defaults
        defaults = {key: value for key, value, *_ in DEFAULT_SETTINGS}

        if self._path.exists():
            try:
                with open(self._path, "r") as f:
                    saved = json.load(f)
                # Merge: saved values override defaults
                defaults.update(saved)
            except (json.JSONDecodeError, OSError) as e:
                print(f"[config] WARNING: Failed to load config.json ({e}), using defaults")

        self._data = defaults
        # Write back so any new default keys are persisted
        self._save()

    def _save(self):
        """Write current config to JSON file."""
        try:
            with open(self._path, "w") as f:
                json.dump(self._data, f, indent=2)
        except OSError as e:
            print(f"[config] Failed to save config: {e}")

    def get(self, key: str, default=None):
        """Fast in-memory read."""
        return self._data.get(key, default)

    async def set(self, key: str, value):
        """Update value in memory and write to disk."""
        async with self._lock:
            self._data[key] = value
            self._save()

    def get_all_grouped(self) -> dict:
        """Return all settings grouped by category for the dashboard."""
        result = {}
        for key, default_val, vtype, category, description in DEFAULT_SETTINGS:
            if category not in result:
                result[category] = []
            result[category].append({
                "key": key,
                "value": self._data.get(key, default_val),
                "value_type": vtype,
                "description": description,
            })
        return result

    def get_setting_meta(self, key: str) -> dict | None:
        """Get full setting metadata for a single key."""
        if key not in _META:
            return None
        vtype, category, description = _META[key]
        return {
            "key": key,
            "value": self._data.get(key),
            "value_type": vtype,
            "category": category,
            "description": description,
        }
