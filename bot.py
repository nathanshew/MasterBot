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
HELP = """📋 *Commands*

*Planner*
/addtask `<title> <time> <priority> [date]`
/addtasks — bulk add, one task per line
/tasks — list pending tasks
/done `<id>` — mark task complete
/log `<id> <time>` — log time on a task
/deltask `<id>` — delete a task
/deltasks `<id1> <id2> ...` — bulk delete
/edittask `<id> <field> <value>` — edit title/priority/time/due
/duetasks `<date> <id1> <id2> ...` — bulk set due date
/today — today's schedule

*Events*
/addevent `<title> <date> <start> <end>`
/events — list upcoming events
/editevent `<id> <field> <value>`
/delevent `<id>`

*Recurring*
/addrecurring `<title> <day> <start> <end>`
/addrecurrings — bulk add, one per line
/recurring — list recurring activities
/skiprecurring `<id> [date]` — skip once (default: today)
/delrecurring `<id>`

*Attendance*
/queryOpenJio — manually trigger attendance check

*Other*
/heartbeat — check bot is alive
/help — this message"""

app.add_handler(CommandHandler(
    "heartbeat", lambda u, c: u.message.reply_text("I am up!"), filters=filters.Chat(chat_id=CHAT_ID)
))
app.add_handler(CommandHandler(
    "help", lambda u, c: u.message.reply_text(HELP, parse_mode='Markdown'),
    filters=filters.Chat(chat_id=CHAT_ID)
))

app.run_polling()
