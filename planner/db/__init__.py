from .connection import cursor
from .tasks import (  # noqa: F401
    add as add_task, get_pending, update as update_task,
    log as log_task, delete as delete_task, delete_many as delete_tasks
)
from .events import add as add_event, get_upcoming, update as update_event, delete as delete_event  # noqa: F401
from .recurring import (  # noqa: F401
    add as add_recurring, get_for_date as get_recurring_for_date,
    get_all as get_all_recurring, delete as delete_recurring, add_skip as skip_recurring
)


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
            CREATE TABLE IF NOT EXISTS recurring_events (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                day_of_week SMALLINT NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL
            );
            CREATE TABLE IF NOT EXISTS recurring_skips (
                recurring_id INTEGER REFERENCES recurring_events(id) ON DELETE CASCADE,
                skip_date DATE NOT NULL,
                PRIMARY KEY (recurring_id, skip_date)
            );
        """)
