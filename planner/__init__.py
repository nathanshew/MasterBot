from .db import init
from .commands import register as _register


def register(app):
    init()
    _register(app)
