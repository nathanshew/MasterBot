from .connection import cursor
from .tasks import add as add_task, get_pending, update as update_task, log as log_task, delete as delete_task, delete_many as delete_tasks  # noqa: F401
from .events import add as add_event, get_upcoming, update as update_event, delete as delete_event  # noqa: F401


def init():
    with cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                priority VARCHAR(4) NOT NULL,
                estimated_minutes INTEGER NOT NULL,
                logged_minutes INTEGER NOT NULL DEFAULT 0,
                done BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
            ALTER TABLE tasks ADD COLUMN IF NOT EXISTS due_date DATE;
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                date DATE NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
