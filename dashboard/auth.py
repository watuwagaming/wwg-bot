"""Simple password-based session auth for the dashboard."""

import hmac
import os
from functools import wraps

from quart import Blueprint, request, session, jsonify

auth_bp = Blueprint("auth", __name__)


def login_required(f):
    @wraps(f)
    async def wrapper(*args, **kwargs):
        if not session.get("authenticated"):
            return jsonify({"error": "unauthorized"}), 401
        return await f(*args, **kwargs)
    return wrapper


@auth_bp.route("/api/login", methods=["POST"])
async def login():
    data = await request.get_json()
    password = data.get("password", "") if data else ""
    expected = os.getenv("DASHBOARD_PASSWORD", "")

    if not expected:
        return jsonify({"error": "DASHBOARD_PASSWORD not set in .env"}), 500

    if hmac.compare_digest(password, expected):
        session["authenticated"] = True
        session.permanent = True
        return jsonify({"ok": True})

    return jsonify({"error": "wrong password"}), 403


@auth_bp.route("/api/logout", methods=["POST"])
async def logout():
    session.clear()
    return jsonify({"ok": True})


@auth_bp.route("/api/me")
async def me():
    if session.get("authenticated"):
        return jsonify({"authenticated": True})
    return jsonify({"authenticated": False}), 401
