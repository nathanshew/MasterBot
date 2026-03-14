from telegram.ext import CommandHandler, filters
from ..db import add_task, get_pending, update_task, log_task, delete_task
from ..utils import fmt, parse_duration

PRIORITY_LABELS = {'high': '🔴 HIGH', 'mid': '🟡 MID', 'low': '🟢 LOW'}


async def cmd_addtask(update, context):
    # /addtask <title> <time> <priority>
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /addtask <title> <time> <priority>\nExample: /addtask Write report 2h high")
        return
    priority = args[-1].lower()
    if priority not in ('high', 'mid', 'low'):
        await update.message.reply_text("Priority must be: high, mid, or low")
        return
    try:
        minutes = parse_duration(args[-2])
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    title = ' '.join(args[:-2])
    task = add_task(title, priority, minutes)
    await update.message.reply_text(f"✅ Task #{task['id']} added: {title} ({fmt(minutes)}, {PRIORITY_LABELS[priority]})")


async def cmd_tasks(update, context):
    tasks = get_pending()
    if not tasks:
        await update.message.reply_text("No pending tasks.")
        return
    lines = ["📋 *Pending tasks:*\n"]
    for t in tasks:
        remaining = t['estimated_minutes'] - t['logged_minutes']
        logged = f" · {fmt(t['logged_minutes'])} logged" if t['logged_minutes'] > 0 else ''
        lines.append(f"#{t['id']} {PRIORITY_LABELS[t['priority']]} — {t['title']} ({fmt(remaining)}{logged})")
    await update.message.reply_text('\n'.join(lines), parse_mode='Markdown')


async def cmd_done(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /done <task_id>")
        return
    task = update_task(int(context.args[0]), done=True)
    if not task:
        await update.message.reply_text("Task not found.")
        return
    await update.message.reply_text(f"✅ Done: {task['title']}")


async def cmd_log(update, context):
    # /log <id> <time>
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /log <task_id> <time>\nExample: /log 3 1h")
        return
    try:
        minutes = parse_duration(context.args[1])
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    task = log_task(int(context.args[0]), minutes)
    if not task:
        await update.message.reply_text("Task not found.")
        return
    remaining = task['estimated_minutes'] - task['logged_minutes']
    status = "done!" if remaining <= 0 else f"{fmt(remaining)} remaining"
    await update.message.reply_text(f"Logged {fmt(minutes)} on #{task['id']} {task['title']} — {status}")


async def cmd_deltask(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /deltask <task_id>")
        return
    deleted = delete_task(int(context.args[0]))
    await update.message.reply_text("🗑 Deleted." if deleted else "Task not found.")


async def cmd_edittask(update, context):
    # /edittask <id> <field> <value>  —  fields: title, priority, time
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /edittask <id> <field> <value>\nFields: title, priority, time")
        return
    task_id = int(context.args[0])
    field = context.args[1].lower()
    value = ' '.join(context.args[2:])

    if field == 'title':
        task = update_task(task_id, title=value)
    elif field == 'priority':
        if value not in ('high', 'mid', 'low'):
            await update.message.reply_text("Priority must be: high, mid, or low")
            return
        task = update_task(task_id, priority=value)
    elif field == 'time':
        try:
            task = update_task(task_id, estimated_minutes=parse_duration(value))
        except ValueError as e:
            await update.message.reply_text(str(e))
            return
    else:
        await update.message.reply_text("Unknown field. Use: title, priority, time")
        return

    if not task:
        await update.message.reply_text("Task not found.")
        return
    await update.message.reply_text(f"✅ Updated #{task['id']}: {task['title']}")


def register(app, chat_id):
    f = filters.Chat(chat_id=chat_id)
    app.add_handler(CommandHandler("addtask", cmd_addtask, filters=f))
    app.add_handler(CommandHandler("tasks", cmd_tasks, filters=f))
    app.add_handler(CommandHandler("done", cmd_done, filters=f))
    app.add_handler(CommandHandler("log", cmd_log, filters=f))
    app.add_handler(CommandHandler("deltask", cmd_deltask, filters=f))
    app.add_handler(CommandHandler("edittask", cmd_edittask, filters=f))
