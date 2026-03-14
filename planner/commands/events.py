from datetime import date
from telegram.ext import CommandHandler, filters
from ..db import add_event, get_upcoming, update_event, delete_event
from ..utils import parse_date, parse_time


async def cmd_addevent(update, context):
    # /addevent <title> <date> <start> <end>
    args = context.args
    if len(args) < 4:
        await update.message.reply_text("Usage: /addevent <title> <date> <start> <end>\nExample: /addevent Standup 13/03 10:00 11:00")
        return
    try:
        end_time = parse_time(args[-1])
        start_time = parse_time(args[-2])
        event_date = parse_date(args[-3])
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    title = ' '.join(args[:-3])
    event = add_event(title, event_date, start_time, end_time)
    await update.message.reply_text(
        f"📅 Event #{event['id']} added: {title} on "
        f"{event_date.strftime('%d %b')} {start_time.strftime('%H:%M')}–{end_time.strftime('%H:%M')}"
    )


async def cmd_events(update, context):
    events = get_upcoming(from_date=date.today())
    if not events:
        await update.message.reply_text("No upcoming events.")
        return
    lines = ["📅 *Upcoming events:*\n"]
    for e in events:
        lines.append(f"#{e['id']} {e['date'].strftime('%d %b')} {e['start_time'].strftime('%H:%M')}–{e['end_time'].strftime('%H:%M')} — {e['title']}")
    await update.message.reply_text('\n'.join(lines), parse_mode='Markdown')


async def cmd_delevent(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /delevent <event_id>")
        return
    deleted = delete_event(int(context.args[0]))
    await update.message.reply_text("🗑 Deleted." if deleted else "Event not found.")


async def cmd_editevent(update, context):
    # /editevent <id> <field> <value>  —  fields: title, date, start, end
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /editevent <id> <field> <value>\nFields: title, date, start, end")
        return
    event_id = int(context.args[0])
    field = context.args[1].lower()
    value = ' '.join(context.args[2:])

    try:
        if field == 'title':
            event = update_event(event_id, title=value)
        elif field == 'date':
            event = update_event(event_id, date=parse_date(value))
        elif field == 'start':
            event = update_event(event_id, start_time=parse_time(value))
        elif field == 'end':
            event = update_event(event_id, end_time=parse_time(value))
        else:
            await update.message.reply_text("Unknown field. Use: title, date, start, end")
            return
    except ValueError as e:
        await update.message.reply_text(str(e))
        return

    if not event:
        await update.message.reply_text("Event not found.")
        return
    await update.message.reply_text(f"✅ Updated event #{event['id']}: {event['title']}")


def register(app, chat_id):
    f = filters.Chat(chat_id=chat_id)
    app.add_handler(CommandHandler("addevent", cmd_addevent, filters=f))
    app.add_handler(CommandHandler("events", cmd_events, filters=f))
    app.add_handler(CommandHandler("delevent", cmd_delevent, filters=f))
    app.add_handler(CommandHandler("editevent", cmd_editevent, filters=f))
