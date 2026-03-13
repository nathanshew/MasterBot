from datetime import date
from telegram.ext import CommandHandler
from ..db import get_pending, get_upcoming
from .. import scheduler


async def cmd_today(update, context):
    tasks = get_pending()
    events = get_upcoming(from_date=date.today())
    result = scheduler.build(tasks, events)
    await update.message.reply_text(scheduler.format(result), parse_mode='Markdown')


def register(app):
    app.add_handler(CommandHandler("today", cmd_today))
