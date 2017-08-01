"""Provide a common interface to the `logging` module."""

import logging

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        """Python-2.6 friendly NullHandler."""

        def emit(self, record):
            """Fake `emit` method."""
            pass


def get_logger(name):
    """Return an initialized logger."""
    log = logging.getLogger(name)
    log.addHandler(NullHandler())
    return log
