class RequestHandler(object):
    def __init__(self, request):
        self.request = request

    def handle_request(self):
        return NotImplemented

    def _handle_true_or_false(self):
        return NotImplemented