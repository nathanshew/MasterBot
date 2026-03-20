from telegram.ext import CommandHandler, filters
from ..db import add_recurring, get_all_recurring, delete_recurring
from ..db.recurring import parse_day
from ..utils import parse_time

DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


async def cmd_addrecurring(update, context):
    # /addrecurring <title> <day> <start> <end>
    args = context.args
    if len(args) < 4:
        await update.message.reply_text(
            "Usage: /addrecurring <title> <day> <start> <end>\n"
            "Example: /addrecurring CS2103 mon 14:00 16:00"
        )
        return
    try:
        end_time = parse_time(args[-1])
        start_time = parse_time(args[-2])
        day = parse_day(args[-3])
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    title = ' '.join(args[:-3])
    r = add_recurring(title, day, start_time, end_time)
    await update.message.reply_text(
        f"🔁 #{r['id']} added: {title} every {DAY_NAMES[day]} "
        f"{start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}"
    )


async def cmd_recurring(update, context):
    rows = get_all_recurring()
    if not rows:
        await update.message.reply_text("No recurring activities.")
        return
    lines = ["🔁 *Recurring activities:*\n"]
    for r in rows:
        t = f"{r['start_time'].strftime('%H:%M')}–{r['end_time'].strftime('%H:%M')}"
        lines.append(f"#{r['id']} {DAY_NAMES[r['day_of_week']]} {t} — {r['title']}")
    await update.message.reply_text('\n'.join(lines), parse_mode='Markdown')


async def cmd_delrecurring(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /delrecurring <id>")
        return
    deleted = delete_recurring(int(context.args[0]))
    await update.message.reply_text("🗑 Deleted." if deleted else "Not found.")


def register(app, chat_id):
    f = filters.Chat(chat_id=chat_id)
    app.add_handler(CommandHandler("addrecurring", cmd_addrecurring, filters=f))
    app.add_handler(CommandHandler("recurring", cmd_recurring, filters=f))
    app.add_handler(CommandHandler("delrecurring", cmd_delrecurring, filters=f))
