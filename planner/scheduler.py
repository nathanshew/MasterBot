from datetime import datetime, date
from .utils import fmt

WORK_TOTAL = 22 * 60 - (8 * 60 + 30)  # 8:30am–10:00pm = 810 min
PRIORITY_ORDER = {'high': 0, 'mid': 1, 'low': 2}
PRIORITY_EMOJI = {'high': '🔴', 'mid': '🟡', 'low': '🟢'}


def _event_minutes(e):
    return (e['end_time'].hour * 60 + e['end_time'].minute) - (e['start_time'].hour * 60 + e['start_time'].minute)


def build(tasks, events):
    today = date.today()
    today_events = sorted([e for e in events if e['date'] == today], key=lambda e: e['start_time'])
    available = WORK_TOTAL - sum(_event_minutes(e) for e in today_events)

    pending = sorted(
        [t for t in tasks if not t['done'] and (t['estimated_minutes'] - t['logged_minutes']) > 0],
        key=lambda t: (PRIORITY_ORDER[t['priority']], t['created_at'])
    )

    scheduled, unscheduled, budget = [], [], available
    for task in pending:
        remaining = task['estimated_minutes'] - task['logged_minutes']
        if budget <= 0:
            unscheduled.append(task)
        else:
            slot = min(remaining, budget)
            scheduled.append({**task, 'slot': slot, 'remaining': remaining})
            budget -= slot

    return {'events': today_events, 'scheduled': scheduled, 'unscheduled': unscheduled, 'available': available, 'leftover': budget}


def format(result):
    lines = [f"📅 *{datetime.now().strftime('%A, %d %b')}*", f"⏰ 8:30am–10:00pm · {fmt(result['available'])} available\n"]

    if result['events']:
        lines.append("📌 *Events:*")
        for e in result['events']:
            lines.append(f"  • {e['start_time'].strftime('%H:%M')}–{e['end_time'].strftime('%H:%M')} {e['title']}")
        lines.append('')

    if result['scheduled']:
        lines.append("✅ *Tasks:*")
        for i, t in enumerate(result['scheduled'], 1):
            time_str = f"{fmt(t['slot'])} of {fmt(t['remaining'])}" if t['slot'] < t['remaining'] else fmt(t['slot'])
            logged = f" · {fmt(t['logged_minutes'])} logged" if t['logged_minutes'] > 0 else ''
            lines.append(f"  {i}. {PRIORITY_EMOJI[t['priority']]} #{t['id']} {t['title']} — {time_str}{logged}")
        if result['leftover'] > 0:
            lines.append(f"\n⏳ {fmt(result['leftover'])} spare")
    else:
        lines.append("✅ No pending tasks!")

    if result['unscheduled']:
        lines.append("\n⏭ *Didn't fit today:*")
        for t in result['unscheduled']:
            lines.append(f"  • {PRIORITY_EMOJI[t['priority']]} #{t['id']} {t['title']} ({fmt(t['estimated_minutes'] - t['logged_minutes'])})")

    return '\n'.join(lines)
