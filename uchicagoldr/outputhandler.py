from uchicagoldr.output import Output


class OutputHandler(object):
    def __init__(self, output_instance):
        assert(isinstance(output_instance, Output))
        self.output_instance = output_instance

    def display_data(self):
        displayer = Displayer(self.output_instance.type_str,
                              self.output_instance.data)
        return displayer.display()

    def handle_requests(self):
        for request in self.requests:
            handler = RequestHandler(request)
            yield handler.handle_request()

    def handle_errors(self):
        raise NotImplemented


class Displayer(object):
    def __init__(self, kind, data):
        self.class_being_displayed = kind
        self.data = data

    def display(self):
        if self.class_being_displayed == 'family':
            return NotImplemented
        if self.class_being_displayed == 'directory':
            return NotImplemented
        if self.class_being_displayed == 'string':
            return NotImplemented
        if self.class_being_displayed == 'item':
            return NotImplemented
        if self.class_being_displayed == 'accessionitem':
            return NotImplemented


class RequestHandler(object):
    def __init__(self, request):
        self.request = request

    def handle_request(self):
        return NotImplemented

    def _handle_true_or_false(self):
        return NotImplemented


class ErrorHandler(object):
    def __init__(self, error):
        self.error = error

    def handle_error(self):
        return NotImplemented

    def _handle_value_error(self):
        return NotImplemented
