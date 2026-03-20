from .connection import cursor

DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']


def parse_day(s):
    s = s.lower()
    full = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    if s in full:
        return full.index(s)
    if s in DAYS:
        return DAYS.index(s)
    if s.isdigit() and 0 <= int(s) <= 6:
        return int(s)
    raise ValueError(f"Invalid day '{s}'. Use mon-sun or monday-sunday.")


def add(title, day_of_week, start_time, end_time):
    with cursor() as cur:
        cur.execute(
            "INSERT INTO recurring_events (title, day_of_week, start_time, end_time)"
            " VALUES (%s, %s, %s, %s) RETURNING *",
            (title, day_of_week, start_time, end_time)
        )
        return cur.fetchone()


def get_for_date(d):
    with cursor() as cur:
        cur.execute(
            "SELECT * FROM recurring_events WHERE day_of_week = %s"
            " AND id NOT IN (SELECT recurring_id FROM recurring_skips WHERE skip_date = %s)"
            " ORDER BY start_time",
            (d.weekday(), d)
        )
        return cur.fetchall()


def add_skip(recurring_id, skip_date):
    with cursor() as cur:
        cur.execute(
            "INSERT INTO recurring_skips (recurring_id, skip_date) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (recurring_id, skip_date)
        )


def get_for_day(day_of_week):
    with cursor() as cur:
        cur.execute(
            "SELECT * FROM recurring_events WHERE day_of_week = %s ORDER BY start_time",
            (day_of_week,)
        )
        return cur.fetchall()


def get_all():
    with cursor() as cur:
        cur.execute("SELECT * FROM recurring_events ORDER BY day_of_week, start_time")
        return cur.fetchall()


def delete(recurring_id):
    with cursor() as cur:
        cur.execute("DELETE FROM recurring_events WHERE id = %s", (recurring_id,))
        return cur.rowcount > 0
