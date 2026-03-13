import os
import asyncio
import threading
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from sheets.checker import Checker
from commands import hi
from commands import query
from jobs import daily_hi
from jobs import attendance_check

load_dotenv(override=True)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
THREAD_ID = os.getenv('TELEGRAM_THREAD_ID')


def build_app():
    app = ApplicationBuilder().token(TOKEN).build()
    checker = Checker(app.bot, CHAT_ID, THREAD_ID)

    hi.register(app)
    query.register(app, checker)
    daily_hi.register(app)
    attendance_check.register(app, checker)

    return app


# ── Local polling mode ────────────────────────────────────────────────────────

def run_polling():
    build_app().run_polling()


# ── Railway / Cloud Run Flask mode ───────────────────────────────────────────

def run_flask():
    from flask import Flask, jsonify
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    import pytz

    TIMEZONE = os.getenv('TIMEZONE', 'Asia/Singapore')
    port = int(os.getenv('PORT', 8080))

    app = ApplicationBuilder().token(TOKEN).build()
    checker = Checker(app.bot, CHAT_ID, THREAD_ID)

    def run_check():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(checker.run())
        finally:
            loop.close()

    flask_app = Flask(__name__)

    @flask_app.route('/', methods=['GET', 'POST'])
    def trigger():
        threading.Thread(target=run_check, daemon=True).start()
        return jsonify({'status': 'ok'}), 200

    @flask_app.route('/health')
    def health():
        return jsonify({'status': 'healthy'}), 200

    scheduler = BackgroundScheduler(timezone=pytz.timezone(TIMEZONE))
    scheduler.add_job(
        run_check,
        CronTrigger(day_of_week='sat', hour=20, minute=0, timezone=TIMEZONE),
    )
    scheduler.start()

    flask_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if 'PORT' in os.environ:
        run_flask()
    else:
        run_polling()
