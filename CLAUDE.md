# MasterBot — Claude Instructions

## Project
Telegram bot built with `python-telegram-bot` + Google Sheets API.
Simple, focused, no unnecessary complexity.

## Stack
- `python-telegram-bot` with job-queue
- `python-dotenv` for config
- Google Sheets API (`google-auth`, `google-api-python-client`)
- Hosted on Railway

## Principles
- **Keep it simple.** No abstractions unless they earn their place.
- **No bloat.** Don't add extra error handling, fallbacks, logging, or validation unless asked.
- **Don't change what wasn't asked.** Only touch the code relevant to the request.
- **Minimal files.** Don't create new files if existing ones work.
- **No comments** unless the logic genuinely isn't obvious.

## Structure
- `bot.py` — entry point, wires everything together
- `commands/` — telegram command handlers (register with app)
- `jobs/` — scheduled jobs (register with app)
- `sheets/` — Google Sheets interaction layer
