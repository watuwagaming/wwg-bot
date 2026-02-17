# Doomsday Bot

A Discord community bot for [Watu wa Gaming](https://www.youtube.com/@watuwagaming). Keeps the server active and entertaining with automated greetings, community engagement features, and a web-based admin dashboard for full control.

## Features

- **Morning Greetings** — Sends a random daily greeting at a configurable time
- **Dead Chat Reviver** — Detects prolonged silence and drops hot takes or conversation starters
- **Game Detection** — Notices when multiple members are playing the same game and suggests they link up
- **GN Police** — Catches people who say goodnight but don't actually leave
- **Hype Detector** — Recognizes when chat is popping off and hypes it up
- **Welcome Hazing** — Gives new members a warm (and slightly unhinged) welcome
- **Late Night Mode** — Special existential vibes for the midnight gamers
- **Reaction Chains** — Piles onto emoji reactions when the community gets one going
- **Modmail** — Forwards DMs to a staff channel and allows staff to reply
- **Status Rotation** — Cycles through custom bot statuses
- **Admin Dashboard** — Web UI to toggle features, adjust settings, view logs, and monitor stats

All feature chances, cooldowns, thresholds, and channel targets are configurable from the dashboard without redeploying.

## Requirements

- Python 3.10+
- A Discord bot token with all intents enabled
- A server (e.g. Digital Ocean droplet) for hosting

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/watuwagaming/wwg-bot.git
cd wwg-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Create a `.env` file in the project root:

```env
TOKEN=your-discord-bot-token
DASHBOARD_PASSWORD=pick-a-strong-password
DASHBOARD_PORT=8080
DASHBOARD_SECRET=any-random-string-for-session-signing
```

| Variable | Description |
|----------|-------------|
| `TOKEN` | Your Discord bot token from the [Developer Portal](https://discord.com/developers/applications) |
| `DASHBOARD_PASSWORD` | Password to log into the admin dashboard |
| `DASHBOARD_PORT` | Port for the dashboard web server (default: `8080`) |
| `DASHBOARD_SECRET` | Random string used to sign session cookies |

### 4. Run the bot

```bash
python main.py
```

On first run, the bot will:
- Create `config.json` with all default settings
- Create `bot.db` (SQLite database for logs and stats)
- Start the dashboard web server

### 5. Access the dashboard

Open `http://YOUR_SERVER_IP:8080` in your browser and log in with your `DASHBOARD_PASSWORD`.

If you're on a Digital Ocean droplet, make sure the port is open:

```bash
ufw allow 8080
```

Or allow it via the Digital Ocean control panel under **Networking > Firewalls**.

## Project Structure

```
wwg-bot/
├── main.py              # Entry point — loads cogs and starts the bot + dashboard
├── bot.py               # Shared bot instance and global references (config, logger)
├── config.py            # Config system — reads/writes config.json
├── database.py          # SQLite schema for logs and stats
├── logger.py            # Logging module for troll and activity tracking
├── helpers.py           # Utility functions shared across cogs
├── messages.py          # All message templates, greetings, troll lines, etc.
├── requirements.txt     # Python dependencies
├── pytest.ini           # Pytest configuration
├── .env                 # Environment variables (not committed)
├── config.json          # Bot settings (auto-generated, not committed)
├── bot.db               # SQLite database for logs (auto-generated, not committed)
├── cogs/
│   ├── background_trolls.py  # Troll loop — periodic background trolls
│   ├── dead_chat.py          # Dead chat reviver
│   ├── events.py             # Member join, presence, reaction events
│   ├── modmail.py            # DM forwarding and staff replies
│   ├── morning_greeting.py   # Daily morning greeting task
│   ├── on_message.py         # Per-message features (GN police, hype, rage, etc.)
│   └── status_rotation.py    # Rotating bot status
├── dashboard/
│   ├── app.py           # Quart web app factory
│   ├── auth.py          # Dashboard login/session auth
│   ├── api.py           # REST API endpoints
│   └── templates/
│       └── index.html   # Dashboard frontend (single-page app)
└── tests/               # Test suite (pytest)
    ├── conftest.py
    ├── test_background_trolls.py
    ├── test_config.py
    ├── test_dead_chat.py
    ├── test_events.py
    ├── test_helpers.py
    ├── test_messages.py
    ├── test_modmail.py
    ├── test_on_message.py
    └── test_structure.py
```

## Dashboard

The admin dashboard lets you control the bot from a web browser:

- **Features** — Toggle any feature on/off, adjust all chances and cooldowns in real time
- **Channels** — Change which channels the bot posts to, manage excluded channels
- **Troll Log** — See every action the bot took, who was involved, with filters and pagination
- **Activity Log** — Full audit trail of greetings, modmail, game detections, etc.
- **Stats** — Counters for every feature, most active targets, daily activity charts

Settings are saved to `config.json` and persist across restarts. Logs and stats are stored in `bot.db` (SQLite).

## Configuration

All settings live in `config.json` which is auto-generated on first run. You can edit it by hand or through the dashboard. The file is a flat key-value JSON object:

```json
{
  "feature.morning_greeting.enabled": true,
  "feature.morning_greeting.hour_min": 6,
  "feature.morning_greeting.hour_max": 10,
  "feature.game_detection.chance": 0.03,
  "channels.general_id": "750702727566327869",
  ...
}
```

If new features are added in a code update, their default settings are automatically merged into your existing `config.json` without overwriting your customizations.

## Discord Bot Setup

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application and add a bot
3. Enable **all three Privileged Gateway Intents**:
   - Presence Intent
   - Server Members Intent
   - Message Content Intent
4. Generate an invite link with these permissions:
   - Manage Nicknames
   - Send Messages
   - Add Reactions
   - Read Message History
   - Embed Links
5. Invite the bot to your server
6. Copy the bot token into your `.env` file

## Dependencies

| Package | Purpose |
|---------|---------|
| `discord.py` | Discord bot framework |
| `pytz` | Timezone handling (Africa/Nairobi) |
| `python-dotenv` | Load environment variables from `.env` |
| `quart` | Async web framework for the dashboard |
| `aiosqlite` | Async SQLite for logs and stats |
| `hypercorn` | ASGI server for the dashboard |

## License

Private repository — Watu wa Gaming.
