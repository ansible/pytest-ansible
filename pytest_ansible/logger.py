import logging

try:
    from logging import NullHandler
except ImportError:
    from logging import Handler

    class NullHandler(Handler):

        def emit(self, record):
            pass


def get_logger(name):
    '''Return an initialized logger.'''
    log = logging.getLogger(name)
    log.addHandler(NullHandler())
    return log
