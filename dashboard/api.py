"""REST API endpoints for the dashboard."""

import time

import discord
from quart import Blueprint, request, jsonify, current_app

from dashboard.auth import login_required

api_bp = Blueprint("api", __name__)

_start_time = time.time()


# ── Settings ──────────────────────────────────────────────

@api_bp.route("/api/settings")
@login_required
async def get_settings():
    config = current_app.bot_config
    grouped = config.get_all_grouped()
    return jsonify(grouped)


@api_bp.route("/api/settings/<path:key>", methods=["PUT"])
@login_required
async def update_setting(key: str):
    config = current_app.bot_config
    meta = config.get_setting_meta(key)
    if not meta:
        return jsonify({"error": "setting not found"}), 404

    data = await request.get_json()
    if not data:
        return jsonify({"error": "invalid or missing JSON body"}), 400
    value = data.get("value")
    if value is None:
        return jsonify({"error": "missing 'value'"}), 400

    # Validate by type
    vtype = meta["value_type"]
    try:
        if vtype == "bool":
            if isinstance(value, str):
                value = value.lower() in ("true", "1", "yes")
            else:
                value = bool(value)
        elif vtype == "int":
            value = int(value)
        elif vtype == "float":
            value = float(value)
            if key.endswith(".chance") or key.endswith("_chance"):
                value = max(0.0, min(1.0, value))
        elif vtype == "string":
            value = str(value)
        # json type passes through as-is
    except (ValueError, TypeError):
        return jsonify({"error": f"invalid value for type {vtype}"}), 400

    await config.set(key, value)
    return jsonify({"ok": True, "key": key, "value": value})


@api_bp.route("/api/settings/bulk", methods=["PUT"])
@login_required
async def update_settings_bulk():
    config = current_app.bot_config
    data = await request.get_json()
    if not data:
        return jsonify({"error": "invalid or missing JSON body"}), 400
    updates = data.get("updates", [])
    results = []
    for item in updates:
        key = item.get("key")
        value = item.get("value")
        if key is None or value is None:
            continue
        meta = config.get_setting_meta(key)
        if not meta:
            continue
        vtype = meta["value_type"]
        try:
            if vtype == "bool":
                if isinstance(value, str):
                    value = value.lower() in ("true", "1", "yes")
                else:
                    value = bool(value)
            elif vtype == "int":
                value = int(value)
            elif vtype == "float":
                value = float(value)
                if key.endswith(".chance") or key.endswith("_chance"):
                    value = max(0.0, min(1.0, value))
            elif vtype == "string":
                value = str(value)
        except (ValueError, TypeError):
            continue
        await config.set(key, value)
        results.append({"key": key, "value": value})
    return jsonify({"ok": True, "updated": results})


# ── Channels ──────────────────────────────────────────────

@api_bp.route("/api/channels/excluded")
@login_required
async def get_excluded_channels():
    config = current_app.bot_config
    excluded = config.get("channels.excluded", [])
    return jsonify({"channels": excluded})


@api_bp.route("/api/channels/excluded", methods=["PUT"])
@login_required
async def set_excluded_channels():
    config = current_app.bot_config
    data = await request.get_json()
    if not data:
        return jsonify({"error": "invalid or missing JSON body"}), 400
    channels = data.get("channels", [])
    # Ensure all are ints
    try:
        channels = [int(c) for c in channels]
    except (ValueError, TypeError):
        return jsonify({"error": "all channel IDs must be numeric"}), 400
    await config.set("channels.excluded", channels)
    return jsonify({"ok": True, "channels": channels})


@api_bp.route("/api/channels/excluded/add", methods=["POST"])
@login_required
async def add_excluded_channel():
    config = current_app.bot_config
    data = await request.get_json()
    if not data:
        return jsonify({"error": "invalid or missing JSON body"}), 400
    channel_id = data.get("channel_id")
    if not channel_id:
        return jsonify({"error": "missing channel_id"}), 400
    try:
        channel_id = int(channel_id)
    except ValueError:
        return jsonify({"error": "channel_id must be numeric"}), 400

    excluded = list(config.get("channels.excluded", []))
    if channel_id not in excluded:
        excluded.append(channel_id)
        await config.set("channels.excluded", excluded)
    return jsonify({"ok": True, "channels": excluded})


@api_bp.route("/api/channels/excluded/<int:channel_id>", methods=["DELETE"])
@login_required
async def remove_excluded_channel(channel_id: int):
    config = current_app.bot_config
    excluded = list(config.get("channels.excluded", []))
    excluded = [c for c in excluded if c != channel_id]
    await config.set("channels.excluded", excluded)
    return jsonify({"ok": True, "channels": excluded})


# ── Logs ──────────────────────────────────────────────────

@api_bp.route("/api/logs/trolls")
@login_required
async def get_troll_logs():
    db = current_app.db
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(max(1, int(request.args.get("limit", 50))), 200)
    except (ValueError, TypeError):
        page, limit = 1, 50
    troll_type = request.args.get("type", "")
    user = request.args.get("user", "")
    offset = (page - 1) * limit

    where_clauses = []
    params = []
    if troll_type:
        where_clauses.append("troll_type = ?")
        params.append(troll_type)
    if user:
        where_clauses.append("(target_user_name LIKE ? OR target_user_id = ?)")
        params.extend([f"%{user}%", user])

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Count
    async with db.execute(f"SELECT COUNT(*) FROM troll_log {where_sql}", params) as cur:
        total = (await cur.fetchone())[0]

    # Fetch
    async with db.execute(
        f"SELECT id, timestamp, troll_type, troll_name, target_user_id, target_user_name, "
        f"channel_id, channel_name, details FROM troll_log {where_sql} "
        f"ORDER BY id DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    ) as cur:
        rows = await cur.fetchall()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0], "timestamp": r[1], "troll_type": r[2], "troll_name": r[3],
            "target_user_id": r[4], "target_user_name": r[5],
            "channel_id": r[6], "channel_name": r[7], "details": r[8],
        })

    return jsonify({"logs": logs, "total": total, "page": page, "limit": limit})


@api_bp.route("/api/logs/activity")
@login_required
async def get_activity_logs():
    db = current_app.db
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(max(1, int(request.args.get("limit", 50))), 200)
    except (ValueError, TypeError):
        page, limit = 1, 50
    event_type = request.args.get("type", "")
    offset = (page - 1) * limit

    where_clauses = []
    params = []
    if event_type:
        where_clauses.append("event_type = ?")
        params.append(event_type)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    async with db.execute(f"SELECT COUNT(*) FROM activity_log {where_sql}", params) as cur:
        total = (await cur.fetchone())[0]

    async with db.execute(
        f"SELECT id, timestamp, event_type, description, channel_id, channel_name, "
        f"user_id, user_name, metadata FROM activity_log {where_sql} "
        f"ORDER BY id DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    ) as cur:
        rows = await cur.fetchall()

    logs = []
    for r in rows:
        logs.append({
            "id": r[0], "timestamp": r[1], "event_type": r[2], "description": r[3],
            "channel_id": r[4], "channel_name": r[5],
            "user_id": r[6], "user_name": r[7], "metadata": r[8],
        })

    return jsonify({"logs": logs, "total": total, "page": page, "limit": limit})


@api_bp.route("/api/logs/trolls/types")
@login_required
async def get_troll_types():
    db = current_app.db
    async with db.execute("SELECT DISTINCT troll_type FROM troll_log ORDER BY troll_type") as cur:
        types = [r[0] for r in await cur.fetchall()]
    return jsonify({"types": types})


@api_bp.route("/api/logs/activity/types")
@login_required
async def get_activity_types():
    db = current_app.db
    async with db.execute("SELECT DISTINCT event_type FROM activity_log ORDER BY event_type") as cur:
        types = [r[0] for r in await cur.fetchall()]
    return jsonify({"types": types})


# ── Stats ─────────────────────────────────────────────────

@api_bp.route("/api/stats")
@login_required
async def get_stats():
    db = current_app.db

    # All counters
    async with db.execute("SELECT key, value FROM stats") as cur:
        counters = {r[0]: r[1] for r in await cur.fetchall()}

    # Trolls by type
    async with db.execute(
        "SELECT troll_type, troll_name, COUNT(*) as cnt FROM troll_log "
        "GROUP BY troll_type, troll_name ORDER BY cnt DESC"
    ) as cur:
        by_type = [{"type": r[0], "name": r[1], "count": r[2]} for r in await cur.fetchall()]

    # Top targets
    async with db.execute(
        "SELECT target_user_name, target_user_id, COUNT(*) as cnt FROM troll_log "
        "WHERE target_user_name IS NOT NULL "
        "GROUP BY target_user_id ORDER BY cnt DESC LIMIT 10"
    ) as cur:
        top_targets = [{"name": r[0], "user_id": r[1], "count": r[2]} for r in await cur.fetchall()]

    # Trolls per day (last 30 days)
    async with db.execute(
        "SELECT DATE(timestamp) as day, COUNT(*) as cnt FROM troll_log "
        "WHERE timestamp >= DATE('now', '-30 days') "
        "GROUP BY day ORDER BY day"
    ) as cur:
        per_day = [{"day": r[0], "count": r[1]} for r in await cur.fetchall()]

    # Activity by hour
    async with db.execute(
        "SELECT CAST(strftime('%H', timestamp) AS INTEGER) as hour, COUNT(*) as cnt "
        "FROM activity_log GROUP BY hour ORDER BY hour"
    ) as cur:
        by_hour = [{"hour": r[0], "count": r[1]} for r in await cur.fetchall()]

    return jsonify({
        "counters": counters,
        "trolls_by_type": by_type,
        "top_targets": top_targets,
        "trolls_per_day": per_day,
        "activity_by_hour": by_hour,
    })


# ── Bot Status ────────────────────────────────────────────

@api_bp.route("/api/bot/status")
@login_required
async def bot_status():
    bot = current_app.bot_client
    uptime_sec = int(time.time() - _start_time)
    hours, remainder = divmod(uptime_sec, 3600)
    minutes, seconds = divmod(remainder, 60)

    guild = bot.guilds[0] if bot.guilds else None
    return jsonify({
        "online": bot.is_ready(),
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "uptime_sec": uptime_sec,
        "guild_name": guild.name if guild else None,
        "member_count": guild.member_count if guild else 0,
        "online_members": sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline) if guild else 0,
        "latency_ms": round(bot.latency * 1000, 1),
    })
