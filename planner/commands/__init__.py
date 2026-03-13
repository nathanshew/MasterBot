from . import tasks, events, today


def register(app):
    tasks.register(app)
    events.register(app)
    today.register(app)
