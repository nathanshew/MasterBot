from datetime import time
from base_job import BaseJob


class AttendanceCheckJob(BaseJob):
    text = ''  # not used — send() is overridden

    def __init__(self, checker):
        self.checker = checker

    async def send(self, context):
        await self.checker.run()

    def register(self, app):
        app.job_queue.run_daily(self.send, time=time(hour=20, minute=30))  # 8 PM SGT


def register(app, checker):
    AttendanceCheckJob(checker).register(app)
