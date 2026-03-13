from telegram.ext import ApplicationBuilder
import os
from dotenv import load_dotenv

from commands import hi
from jobs import daily_hi

load_dotenv(override=True)

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

# Register commands
for cmd in [hi]:
    cmd.register(app)

# Register jobs
for job in [daily_hi]:
    job.register(app)

app.run_polling()
