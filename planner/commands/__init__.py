from . import tasks, events, today, recurring


def register(app, chat_id):
    tasks.register(app, chat_id)
    events.register(app, chat_id)
    today.register(app, chat_id)
    recurring.register(app, chat_id)
