from datetime import datetime, timedelta
from sheets.client import _parse_date


# ── Section builders ──────────────────────────────────────────────────────────

def header(col_indices, counts):
    dates = ', '.join(f"{d} ({counts.get(i, 0)})" for i, d in col_indices)
    return (
        "⚠️ *PLEASE KEEP THIS PRIVATE, DO NOT FORWARD* ⚠️\n\n"
        f"📊 *Attendance Alert*\n"
        f"Dates: {dates}\n"
    )


def absent_section(absent, db):
    if not absent:
        return ''

    groups, ungrouped = {}, []
    for name in absent:
        contact = _db_lookup(name, db, 1)
        if contact:
            groups.setdefault(contact, []).append(name)
        else:
            ungrouped.append(name)

    lines = ["\n😢 *Absent for last 3 sessions:*", "_(⭐ = not special care)_\n"]
    for contact, members in groups.items():
        lines.append(f"*{contact}*")
        for i, name in enumerate(members, 1):
            star = '' if _is_special_care(name, db) else ' ⭐'
            lines.append(f"{i}. {name}{star}")
        lines.append('')
    for name in ungrouped:
        star = '' if _is_special_care(name, db) else ' ⭐'
        lines.append(f"• {name}{star}")

    return '\n'.join(lines)


def special_care_section(special_care, db):
    if not special_care:
        return ''

    groups = {}
    for name, att in special_care:
        contact = _db_lookup(name, db, 1) or '—'
        groups.setdefault(contact, []).append((name, att))

    lines = ["\n⭐ *Special Care — Last 3 Sessions:*\n"]
    for contact, members in groups.items():
        lines.append(f"*{contact}*")
        for name, att in members:
            emojis = ' '.join('✅' if p else '❌' for p in att)
            lines.append(f"  {name}: {emojis}")
        lines.append('')

    return '\n'.join(lines)


def birthdays_section(db):
    upcoming = _upcoming_birthdays(db)
    if not upcoming:
        return ''

    lines = ["🎂 *Upcoming Birthdays (This Week):*"]
    for name, d in upcoming:
        lines.append(f"{d.strftime('%a')}: {name} ({d.strftime('%d %b')})")

    return '\n'.join(lines)


def no_absences(col_indices, counts):
    dates = ', '.join(f"{d} ({counts.get(i, 0)})" for i, d in col_indices)
    return (
        "✅ *Attendance Check Complete*\n\n"
        "No members with 3 consecutive absences.\n"
        f"Dates checked: {dates}"
    )


# ── Shared db helpers (used by checker too) ───────────────────────────────────

def _db_lookup(name, db, col):
    for row in db:
        if row and row[0].strip() == name and len(row) > col:
            return row[col].strip()
    return ''


def _is_special_care(name, db):
    return _db_lookup(name, db, 13).lower() == 'yes'


def _ignore_until(name, db):
    val = _db_lookup(name, db, 14)
    if val:
        d = _parse_date(val)
        if d and d.date() > datetime.now().date():
            return True
    return False


def _upcoming_birthdays(db):
    today = datetime.now().date()
    week_end = today + timedelta(days=7)
    found = []
    for row in db:
        name = row[0].strip() if row else ''
        bday_str = row[4].strip() if len(row) > 4 else ''
        if not name or not bday_str:
            continue
        d = _parse_date(bday_str)
        if not d:
            continue
        this_year = d.replace(year=today.year).date()
        if this_year < today:
            this_year = d.replace(year=today.year + 1).date()
        if today <= this_year <= week_end:
            found.append((name, this_year))
    found.sort(key=lambda x: x[1])
    return found
