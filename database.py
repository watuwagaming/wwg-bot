"""SQLite database module for logs and stats only."""

import aiosqlite

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS troll_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    troll_type TEXT NOT NULL,
    troll_name TEXT NOT NULL,
    target_user_id TEXT,
    target_user_name TEXT,
    channel_id TEXT,
    channel_name TEXT,
    details TEXT
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    channel_id TEXT,
    channel_name TEXT,
    user_id TEXT,
    user_name TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS stats (
    key TEXT PRIMARY KEY,
    value INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);
"""

DEFAULT_STATS = [
    "messages_processed",
    "trolls_triggered",
    "trolls_bg_triggered",
    "greetings_sent",
    "dead_chat_revives",
    "gn_callouts",
    "hype_detections",
    "welcomes_sent",
    "game_detections",
    "typing_callouts",
    "reaction_chains",
    "rage_detections",
    "excuse_generations",
    "cap_alarms",
    "flex_polices",
    "lag_defenses",
    "essay_detections",
    "k_energy_fires",
    "late_night_bonuses",
    "modmail_received",
    "modmail_replied",
    "per_message_trolls",
]


async def init_db(db_path: str = "bot.db") -> aiosqlite.Connection:
    """Open database, create tables, seed default stats, return connection."""
    db = await aiosqlite.connect(db_path)
    await db.execute("PRAGMA journal_mode=WAL")

    for statement in CREATE_TABLES_SQL.strip().split(";"):
        statement = statement.strip()
        if statement:
            await db.execute(statement)
    await db.commit()

    # Seed default stats
    now = "1970-01-01T00:00:00"
    for stat_key in DEFAULT_STATS:
        await db.execute(
            "INSERT OR IGNORE INTO stats (key, value, updated_at) VALUES (?, 0, ?)",
            (stat_key, now),
        )

    await db.commit()
    return db
