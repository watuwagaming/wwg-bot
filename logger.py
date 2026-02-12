"""Logging module: troll logs, activity logs, and stats counters."""

import json
import asyncio
from datetime import datetime, timezone

import aiosqlite


class BotLogger:
    def __init__(self, db: aiosqlite.Connection):
        self._db = db
        self._msg_counter = 0
        self._msg_flush_threshold = 100
        self._lock = asyncio.Lock()

    async def log_troll(
        self,
        troll_type: str,
        troll_name: str,
        target_user=None,
        channel=None,
        details: dict | None = None,
    ):
        """Log a troll event to troll_log and increment stats."""
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT INTO troll_log (timestamp, troll_type, troll_name, target_user_id, "
            "target_user_name, channel_id, channel_name, details) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                now,
                troll_type,
                troll_name,
                str(target_user.id) if target_user else None,
                getattr(target_user, "display_name", None),
                str(channel.id) if channel else None,
                getattr(channel, "name", None),
                json.dumps(details) if details else None,
            ),
        )
        await self._db.commit()
        await self.increment_stat("trolls_triggered")

    async def log_activity(
        self,
        event_type: str,
        description: str,
        channel=None,
        user=None,
        metadata: dict | None = None,
    ):
        """Log a general activity event."""
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "INSERT INTO activity_log (timestamp, event_type, description, channel_id, "
            "channel_name, user_id, user_name, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                now,
                event_type,
                description,
                str(channel.id) if channel else None,
                getattr(channel, "name", None),
                str(user.id) if user else None,
                getattr(user, "display_name", str(user) if user else None),
                json.dumps(metadata) if metadata else None,
            ),
        )
        await self._db.commit()

    async def increment_stat(self, key: str, amount: int = 1):
        """Atomically increment a stat counter."""
        now = datetime.now(timezone.utc).isoformat()
        await self._db.execute(
            "UPDATE stats SET value = value + ?, updated_at = ? WHERE key = ?",
            (amount, now, key),
        )
        await self._db.commit()

    async def count_message(self):
        """Batched message counter - flushes to DB every N messages."""
        self._msg_counter += 1
        if self._msg_counter >= self._msg_flush_threshold:
            async with self._lock:
                count = self._msg_counter
                self._msg_counter = 0
            await self.increment_stat("messages_processed", count)

    async def flush_messages(self):
        """Flush remaining message count to DB (call on shutdown)."""
        async with self._lock:
            count = self._msg_counter
            self._msg_counter = 0
        if count > 0:
            await self.increment_stat("messages_processed", count)
