from .masterlog import spawn_logger
from sys import exc_info
from traceback import TracebackException, print_exc

log = spawn_logger(__name__)

class ExceptionHandler(object):

    _log_exceptions = None
    _raise_exceptions = None

    def __init__(self, log_exceptions=True, raise_exceptions=False):
        self.log_exceptions = log_exceptions
        self.raise_exceptions = raise_exceptions

    def handle(self, e, log_exceptions=None, raise_exceptions=None):
        if not isinstance(e, Exception):
            raise ValueError("THE EXCEPTION HANDLER ONLY HANDLES EXCEPTIONS")
        if log_exceptions is None:
            log_exceptions = self.log_exceptions
        if raise_exceptions is None:
            raise_exceptions = self.raise_exceptions

        if log_exceptions:
            exc_type, exc_value, exc_traceback = exc_info()
            tb = TracebackException(exc_type, exc_value, exc_traceback)
            log.critical("".join([x for x in tb.format()]))
        if raise_exceptions:
            raise(e)

    def get_log_exceptions(self):
        return self._log_exceptions

    def set_log_exceptions(self, x):
        self._log_exceptions = bool(x)

    def get_raise_exceptions(self):
        return self._raise_exceptions

    def set_raise_exceptions(self, x):
        self._raise_exceptions = bool(x)

    log_exceptions = property(get_log_exceptions, set_log_exceptions)
    raise_exceptions = property(get_raise_exceptions, set_raise_exceptions)
