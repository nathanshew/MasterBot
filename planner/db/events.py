from .connection import cursor

ALLOWED = {'title', 'date', 'start_time', 'end_time'}


def add(title, date, start_time, end_time):
    with cursor() as cur:
        cur.execute(
            "INSERT INTO events (title, date, start_time, end_time) VALUES (%s, %s, %s, %s) RETURNING *",
            (title, date, start_time, end_time)
        )
        return cur.fetchone()


def get_upcoming(from_date):
    with cursor() as cur:
        cur.execute("SELECT * FROM events WHERE date >= %s ORDER BY date, start_time", (from_date,))
        return cur.fetchall()


def update(event_id, **fields):
    fields = {k: v for k, v in fields.items() if k in ALLOWED}
    if not fields:
        return None
    clause = ', '.join(f"{k} = %s" for k in fields)
    with cursor() as cur:
        cur.execute(f"UPDATE events SET {clause} WHERE id = %s RETURNING *", (*fields.values(), event_id))
        return cur.fetchone()


def delete(event_id):
    with cursor() as cur:
        cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
        return cur.rowcount > 0
