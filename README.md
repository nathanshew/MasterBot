# Telegram Bot Template

A Python Telegram bot template with a modular structure for commands and scheduled jobs.

## Project Structure

```
├── bot.py              # Entry point — registers all commands and jobs
├── commands/           # User-triggered handlers (e.g. /hi)
│   └── hi.py
├── jobs/               # Scheduled tasks
│   ├── base.py         # BaseJob class — extend this for new jobs
│   └── daily_hi.py
├── .env.example        # Environment variable template
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

Fill in `.env`:
- `TELEGRAM_BOT_TOKEN` — get from [@BotFather](https://t.me/BotFather)
- `CHAT_ID` — your target chat ID (use `-100` prefix for supergroups, e.g. `-1002555330539`)
- `THREAD_ID` — (optional) topic/thread ID for supergroups with topics

### 3. Run locally
```bash
python bot.py
```

## Adding a Command

Create `commands/yourcommand.py`:
```python
from telegram.ext import CommandHandler

async def yourcommand(update, context):
    await update.message.reply_text("Your response")

def register(app):
    app.add_handler(CommandHandler("yourcommand", yourcommand))
```

Then in `bot.py`, add it to the commands list:
```python
from commands import hi, yourcommand

for cmd in [hi, yourcommand]:
    cmd.register(app)
```

## Adding a Scheduled Job

Create `jobs/yourjob.py`:
```python
from datetime import time
from jobs.base import BaseJob

class YourJob(BaseJob):
    text = "Your scheduled message"

    def register(self, app):
        app.job_queue.run_daily(self.send, time=time(hour=1, minute=0))  # 9am SGT

def register(app):
    YourJob().register(app)
```

Then in `bot.py`, add it to the jobs list:
```python
from jobs import daily_hi, yourjob

for job in [daily_hi, yourjob]:
    job.register(app)
```

## Deployment

This template is designed to deploy on [Railway](https://railway.app):
1. Push to GitHub
2. Connect repo on Railway
3. Set environment variables in Railway dashboard
4. Railway auto-deploys on every push
