class LDRError(object):
    source = None
    label = ""
    message = ""

    def __init__(self, exception):
        assert isinstance(exception, Exception)
        self.source = exception
        self.label = exception.__name__
        self.message = exception.__message__

    def get_label(self):
        return self.label

    def get_message(self):
        return self.message