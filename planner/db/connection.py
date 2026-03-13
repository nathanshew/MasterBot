import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


@contextmanager
def cursor():
    c = psycopg2.connect(os.getenv('DATABASE_URL'))
    try:
        with c.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()
