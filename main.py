"""WWG Bot entry point — loads cogs and runs the bot."""

import asyncio
import os

from dotenv import load_dotenv

import bot as shared
from config import BotConfig
from database import init_db
from logger import BotLogger
from dashboard.app import create_app

load_dotenv()

EXTENSIONS = [
    "cogs.background_trolls",
    "cogs.dead_chat",
    "cogs.morning_greeting",
    "cogs.status_rotation",
    "cogs.events",
    "cogs.modmail",
    "cogs.on_message",
]


@shared.client.event
async def on_ready():
    print("Bot's Ready")

    # Initialize config (JSON file) and database (SQLite for logs/stats)
    shared.config = BotConfig()
    shared.config.load()
    db = await init_db()
    shared.logger = BotLogger(db)

    # Start dashboard
    dashboard_port = int(os.getenv("DASHBOARD_PORT", "8080"))
    app = create_app(shared.config, db, shared.client)

    from hypercorn.asyncio import serve
    from hypercorn.config import Config as HyperConfig
    hyper_config = HyperConfig()
    hyper_config.bind = [f"0.0.0.0:{dashboard_port}"]
    hyper_config.accesslog = None  # suppress access logs
    asyncio.create_task(serve(app, hyper_config))
    print(f"Dashboard running on http://0.0.0.0:{dashboard_port}")

    # Load all cogs
    for ext in EXTENSIONS:
        await shared.client.load_extension(ext)


shared.client.run(os.getenv("TOKEN"))
