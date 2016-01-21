class ErrorHandler(object):
    def __init__(self, error):
        self.error = error

    def handle_error(self):
        return NotImplemented

    def _handle_value_error(self):
        return NotImplemented