from uchicagoldr.output import Output


class OutputHandler(object):
    def __init__(self, output_instance):
        assert(isinstance(output_instance, Output))
        self.output_instance = output_instance
        self.displayer = Displayer
        self.requesthandler = RequestHandler
        self.errorhandler = ErrorHandler

    def display_data(self):
        displayer = self.displayer(self.output_instance.type_str,
                              self.output_instance.data)
        return displayer.display()

    def handle_requests(self):
        for request in self.requests:
            handler = self.requesthandler(request)
            yield handler.handle_request()

    def handle_errors(self):
        handler = self.errorhandler(self.output.error)
        return handler.handle_error()


