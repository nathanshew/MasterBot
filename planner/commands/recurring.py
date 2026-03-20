from datetime import date
from telegram.ext import CommandHandler, filters
from ..db import add_recurring, get_all_recurring, delete_recurring, delete_all_recurring, skip_recurring
from ..db.recurring import parse_day
from ..utils import parse_time, parse_date

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


async def cmd_addrecurrings(update, context):
    # /addrecurrings
    # One per line: <title> <day> <start> <end>
    lines = update.message.text.split('\n')[1:]
    lines = [line.strip() for line in lines if line.strip()]
    if not lines:
        await update.message.reply_text(
            "Usage: /addrecurrings\n<title> <day> <start> <end>\n<title> <day> <start> <end>\n..."
        )
        return
    results = []
    for line in lines:
        args = line.split()
        if len(args) < 4:
            results.append(f"❌ {line!r} — need: <title> <day> <start> <end>")
            continue
        try:
            end_time = parse_time(args[-1])
            start_time = parse_time(args[-2])
            day = parse_day(args[-3])
        except ValueError as e:
            results.append(f"❌ {line!r} — {e}")
            continue
        title = ' '.join(args[:-3])
        r = add_recurring(title, day, start_time, end_time)
        results.append(
            f"✅ #{r['id']} {title} every {DAY_NAMES[day]} "
            f"{start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}"
        )
    await update.message.reply_text('\n'.join(results))


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


async def cmd_clearrecurrings(update, context):
    count = delete_all_recurring()
    await update.message.reply_text(f"🗑 Cleared {count} recurring activities.")


async def cmd_delrecurring(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /delrecurring <id>")
        return
    deleted = delete_recurring(int(context.args[0]))
    await update.message.reply_text("🗑 Deleted." if deleted else "Not found.")


async def cmd_skiprecurring(update, context):
    # /skiprecurring <id> [date]  — skip for today or a specific date
    if not context.args:
        await update.message.reply_text("Usage: /skiprecurring <id> [date]\nExample: /skiprecurring 2 21/03")
        return
    try:
        recurring_id = int(context.args[0])
        skip_date = parse_date(context.args[1]) if len(context.args) > 1 else date.today()
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    skip_recurring(recurring_id, skip_date)
    await update.message.reply_text(f"⏭ Skipped #{recurring_id} for {skip_date.strftime('%d %b')}.")


def register(app, chat_id):
    f = filters.Chat(chat_id=chat_id)
    app.add_handler(CommandHandler("addrecurring", cmd_addrecurring, filters=f))
    app.add_handler(CommandHandler("addrecurrings", cmd_addrecurrings, filters=f))
    app.add_handler(CommandHandler("recurring", cmd_recurring, filters=f))
    app.add_handler(CommandHandler("clearrecurrings", cmd_clearrecurrings, filters=f))
    app.add_handler(CommandHandler("delrecurring", cmd_delrecurring, filters=f))
    app.add_handler(CommandHandler("skiprecurring", cmd_skiprecurring, filters=f))
