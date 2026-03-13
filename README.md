# OpenJio Telegram Bot

Telegram bot that checks Google Sheets attendance and sends weekly alerts every Saturday at 8:30 PM SGT.

## Project Structure

```
├── bot.py              # Entry point — wires commands, jobs, and runs the bot
├── commands/
│   ├── hi.py           # /hi — health check
│   └── query.py        # /query — trigger an attendance check manually
├── jobs/
│   ├── base.py         # BaseJob — extend this for new scheduled jobs
│   ├── daily_hi.py     # Daily alive ping
│   └── attendance_check.py  # Saturday 8:30 PM attendance check
├── sheets/
│   ├── auth.py         # Google OAuth (env var or local file)
│   ├── client.py       # Fetches rows from Google Sheets
│   ├── checker.py      # Orchestrates the attendance check
│   └── formatter.py    # Builds each section of the Telegram message
├── .env.example
└── requirements.txt
```

## Setup

### 1. Clone and install
```bash
git clone <your-repo>
cd <your-repo>
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```

Fill in `.env` — see `.env.example` for all variables and descriptions.

### 3. Google credentials (local dev)
1. Go to [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials
2. Create an OAuth 2.0 Client ID (Desktop app) and download `credentials.json`
3. Place `credentials.json` in the project root
4. On first run, a browser window will open to authorise — this creates `token.json`

For Railway, paste the contents of `token.json` into the `GOOGLE_TOKEN_JSON` env var.

### 4. Run locally
```bash
python bot.py
```

## Deployment (Railway)

1. Push to GitHub
2. Connect repo on Railway
3. Set all env vars from `.env.example` in the Railway dashboard
4. Set `GOOGLE_TOKEN_JSON` to the contents of your `token.json`
5. Railway auto-deploys on every push — `PORT` is set automatically

## Adding a Command

Create `commands/yourcommand.py`:
```python
from telegram.ext import CommandHandler

def register(app):
    async def yourcommand(update, context):
        await update.message.reply_text("Your response")
    app.add_handler(CommandHandler("yourcommand", yourcommand))
```

Then import and register it in `bot.py`.

## Adding a Scheduled Job

Create `jobs/yourjob.py`:
```python
from datetime import time
from jobs.base import BaseJob

class YourJob(BaseJob):
    text = "Your scheduled message"

    def register(self, app):
        app.job_queue.run_daily(self.send, time=time(hour=13, minute=0))  # 9 PM SGT

def register(app):
    YourJob().register(app)
```

Then import and register it in `bot.py`.
