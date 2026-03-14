from .db import init
from .commands import register as _register


def register(app, chat_id):
    init()
    _register(app, chat_id)
