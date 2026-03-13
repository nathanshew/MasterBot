from datetime import time
from jobs.base import BaseJob


class DailyHi(BaseJob):
    text = "Hi bot is alive!"

    def register(self, app):
        app.job_queue.run_daily(self.send, time=time(hour=1, minute=0))  # 1:00 UTC = 9am SGT


def register(app):
    DailyHi().register(app)
