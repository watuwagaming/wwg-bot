"""Quart app factory for the dashboard."""

import os
from datetime import timedelta

from quart import Quart, render_template

from dashboard.auth import auth_bp
from dashboard.api import api_bp


def create_app(config, db, bot_client):
    app = Quart(__name__, template_folder="templates")
    app.secret_key = os.getenv("DASHBOARD_SECRET", os.urandom(32).hex())
    app.permanent_session_lifetime = timedelta(days=7)

    # Make config, db, and bot accessible to API routes
    app.bot_config = config
    app.db = db
    app.bot_client = bot_client

    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)

    @app.route("/")
    async def index():
        return await render_template("index.html")

    return app
