
class ErrorPackager(object):
    class Error(object):
        def __init__(self, category, message):
            self.category = category
            self.message = message

        def __str__(self):
            return "category: {}\nmessage: {}".format(self.category,
                                                      self.message)

    def __init__(self):
        self.errors = []

    def get_errors(self):
        return self._errors

    def set_errors(self, value):
        self._errors = value

    def add_error(self, category, message):
        new_error = self.Error(category, message)
        self.errors.append(new_error)

    errors = property(get_errors, set_errors)
