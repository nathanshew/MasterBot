from datetime import date
from telegram.ext import CommandHandler, filters
from ..db import add_task, get_pending, update_task, log_task, delete_task, delete_tasks
from ..utils import fmt, parse_duration, parse_date

PRIORITY_LABELS = {'high': '🔴 HIGH', 'mid': '🟡 MID', 'low': '🟢 LOW'}


def _due_label(due_date):
    if not due_date:
        return ''
    today = date.today()
    if due_date < today:
        return f' · 🚨 overdue ({due_date.strftime("%d/%m")})'
    if due_date == today:
        return ' · ⚠️ due today'
    return f' · due {due_date.strftime("%d/%m")}'


def _parse_task_args(args):
    """Parse title, time, priority, optional due_date from args list."""
    if len(args) < 3:
        return None, None, None, None, "Need at least: <title> <time> <priority>"
    due_date = None
    # Check if last arg is a date
    try:
        due_date = parse_date(args[-1])
        args = args[:-1]
    except ValueError:
        pass
    if len(args) < 3:
        return None, None, None, None, "Need at least: <title> <time> <priority>"
    priority = args[-1].lower()
    if priority not in ('high', 'mid', 'low'):
        return None, None, None, None, "Priority must be: high, mid, or low"
    try:
        minutes = parse_duration(args[-2])
    except ValueError as e:
        return None, None, None, None, str(e)
    title = ' '.join(args[:-2])
    if not title:
        return None, None, None, None, "Title can't be empty"
    return title, minutes, priority, due_date, None


async def cmd_addtask(update, context):
    # /addtask <title> <time> <priority> [date]
    title, minutes, priority, due_date, err = _parse_task_args(list(context.args))
    if err:
        await update.message.reply_text(f"Usage: /addtask <title> <time> <priority> [date]\n{err}")
        return
    task = add_task(title, priority, minutes, due_date)
    due = _due_label(task['due_date'])
    await update.message.reply_text(
        f"✅ Task #{task['id']} added: {title} ({fmt(minutes)}, {PRIORITY_LABELS[priority]}{due})"
    )


async def cmd_addtasks(update, context):
    # /addtasks
    # One task per line: <title> <time> <priority> [date]
    lines = update.message.text.split('\n')[1:]
    lines = [ln.strip() for ln in lines if ln.strip()]
    if not lines:
        await update.message.reply_text(
            "Usage: /addtasks\n<title> <time> <priority> [date]\n<title> <time> <priority> [date]\n..."
        )
        return
    results = []
    for line in lines:
        title, minutes, priority, due_date, err = _parse_task_args(line.split())
        if err:
            results.append(f"❌ {line!r} — {err}")
        else:
            task = add_task(title, priority, minutes, due_date)
            due = _due_label(task['due_date'])
            results.append(f"✅ #{task['id']} {title} ({fmt(minutes)}, {PRIORITY_LABELS[priority]}{due})")
    await update.message.reply_text('\n'.join(results))


async def cmd_tasks(update, context):
    tasks = get_pending()
    if not tasks:
        await update.message.reply_text("No pending tasks.")
        return
    lines = ["📋 *Pending tasks:*\n"]
    for t in tasks:
        remaining = t['estimated_minutes'] - t['logged_minutes']
        logged = f" · {fmt(t['logged_minutes'])} logged" if t['logged_minutes'] > 0 else ''
        due = _due_label(t['due_date'])
        lines.append(f"#{t['id']} {PRIORITY_LABELS[t['priority']]} — {t['title']} ({fmt(remaining)}{logged}{due})")
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


async def cmd_deltasks(update, context):
    # /deltasks 1 2 3
    if not context.args:
        await update.message.reply_text("Usage: /deltasks <id1> <id2> ...")
        return
    try:
        ids = [int(a) for a in context.args]
    except ValueError:
        await update.message.reply_text("IDs must be integers.")
        return
    deleted = delete_tasks(ids)
    msg = f"🗑 Deleted {len(deleted)}: {', '.join(f'#{i}' for i in deleted)}" if deleted else "No tasks found."
    await update.message.reply_text(msg)


async def cmd_edittask(update, context):
    # /edittask <id> <field> <value>  —  fields: title, priority, time, due
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /edittask <id> <field> <value>\nFields: title, priority, time, due")
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
    elif field == 'due':
        try:
            task = update_task(task_id, due_date=parse_date(value))
        except ValueError as e:
            await update.message.reply_text(str(e))
            return
    else:
        await update.message.reply_text("Unknown field. Use: title, priority, time, due")
        return

    if not task:
        await update.message.reply_text("Task not found.")
        return
    await update.message.reply_text(f"✅ Updated #{task['id']}: {task['title']}")


async def cmd_duetasks(update, context):
    # /duetasks <date> <id1> <id2> ...
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /duetasks <date> <id1> <id2> ...\nExample: /duetasks 15/03 1 2 3")
        return
    try:
        due_date = parse_date(context.args[0])
        ids = [int(a) for a in context.args[1:]]
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    results = []
    for task_id in ids:
        task = update_task(task_id, due_date=due_date)
        results.append(f"✅ #{task_id} {task['title']}" if task else f"❌ #{task_id} not found")
    await update.message.reply_text('\n'.join(results))


def register(app, chat_id):
    f = filters.Chat(chat_id=chat_id)
    app.add_handler(CommandHandler("addtask", cmd_addtask, filters=f))
    app.add_handler(CommandHandler("addtasks", cmd_addtasks, filters=f))
    app.add_handler(CommandHandler("tasks", cmd_tasks, filters=f))
    app.add_handler(CommandHandler("done", cmd_done, filters=f))
    app.add_handler(CommandHandler("log", cmd_log, filters=f))
    app.add_handler(CommandHandler("deltask", cmd_deltask, filters=f))
    app.add_handler(CommandHandler("deltasks", cmd_deltasks, filters=f))
    app.add_handler(CommandHandler("duetasks", cmd_duetasks, filters=f))
    app.add_handler(CommandHandler("edittask", cmd_edittask, filters=f))
