import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

import qntq_attendance
import heartbeat
import planner

load_dotenv(override=True)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
THREAD_ID = os.getenv('TELEGRAM_THREAD_ID')

app = ApplicationBuilder().token(TOKEN).build()

qntq_attendance.register(app, app.bot, CHAT_ID, THREAD_ID)
heartbeat.register(app)
planner.register(app)

app.run_polling()
