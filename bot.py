import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from sheets.checker import Checker
from commands import query
from jobs import attendance_check

load_dotenv(override=True)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
THREAD_ID = os.getenv('TELEGRAM_THREAD_ID')

app = ApplicationBuilder().token(TOKEN).build()
checker = Checker(app.bot, CHAT_ID, THREAD_ID)

query.register(app, checker)
attendance_check.register(app, checker)

app.run_polling()
