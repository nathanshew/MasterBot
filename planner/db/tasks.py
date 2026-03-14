from .connection import cursor

ALLOWED = {'title', 'priority', 'estimated_minutes', 'logged_minutes', 'done', 'due_date'}


def add(title, priority, estimated_minutes, due_date=None):
    with cursor() as cur:
        cur.execute(
            "INSERT INTO tasks (title, priority, estimated_minutes, due_date) VALUES (%s, %s, %s, %s) RETURNING *",
            (title, priority, estimated_minutes, due_date)
        )
        return cur.fetchone()


def get_pending():
    with cursor() as cur:
        cur.execute("SELECT * FROM tasks WHERE done = FALSE ORDER BY due_date NULLS LAST, created_at")
        return cur.fetchall()


def update(task_id, **fields):
    fields = {k: v for k, v in fields.items() if k in ALLOWED}
    if not fields:
        return None
    clause = ', '.join(f"{k} = %s" for k in fields)
    with cursor() as cur:
        cur.execute(f"UPDATE tasks SET {clause} WHERE id = %s RETURNING *", (*fields.values(), task_id))
        return cur.fetchone()


def log(task_id, minutes):
    with cursor() as cur:
        cur.execute(
            "UPDATE tasks SET logged_minutes = logged_minutes + %s WHERE id = %s RETURNING *",
            (minutes, task_id)
        )
        return cur.fetchone()


def delete(task_id):
    with cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        return cur.rowcount > 0


def delete_many(task_ids):
    with cursor() as cur:
        cur.execute("DELETE FROM tasks WHERE id = ANY(%s) RETURNING id", (list(task_ids),))
        return [r['id'] for r in cur.fetchall()]
