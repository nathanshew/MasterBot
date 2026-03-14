from .checker import Checker
from . import command, job


def register(app, bot, chat_id, thread_id):
    checker = Checker(bot, chat_id, thread_id)
    command.register(app, checker, chat_id)
    job.register(app, checker)
