from . import tasks, events, today


def register(app, chat_id):
    tasks.register(app, chat_id)
    events.register(app, chat_id)
    today.register(app, chat_id)
