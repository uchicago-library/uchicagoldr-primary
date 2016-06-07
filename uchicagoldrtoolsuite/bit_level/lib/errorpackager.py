
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
        self.numErrors = 0

    def get_errors(self):
        return self._errors

    def set_errors(self, value):
        self._errors = value

    def add(self, category, message):
        new_error = self.Error(category, message)
        self.numErrors += 1
        self.errors.append(new_error)

    def display(self):
        output = []
        for n_error in self.errors:
            output.append(str(n_error))
        return output

    errors = property(get_errors, set_errors)
