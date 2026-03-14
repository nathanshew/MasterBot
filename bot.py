import os
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, filters

import qntq_attendance
import planner

load_dotenv(override=True)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID'))
THREAD_ID = os.getenv('TELEGRAM_THREAD_ID')

app = ApplicationBuilder().token(TOKEN).build()

qntq_attendance.register(app, app.bot, CHAT_ID, THREAD_ID)
planner.register(app, CHAT_ID)
app.add_handler(CommandHandler("heartbeat", lambda u, c: u.message.reply_text("I am up1!"), filters=filters.Chat(chat_id=CHAT_ID)))

app.run_polling()
