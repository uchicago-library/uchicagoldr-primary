from uchicagoldr.error import LDRError, LDRNonFatal, LDRFatal
from uchicagoldr.convenience import get_valid_types
from uchicagoldr.request import Request

class Output(object):
    _type_string = None
    _status = None
    errors = []
    requests = []
    data  = None

    def __init__(self, type_string, status=False):
        if type_string in get_valid_types():
            self._type_string = type_string
        else:
            self._type_string = None
        if status:
            self._status = status
        else:
            self._status = None
        self.data = None
        self.requests = []
        self.errors = []

    def add_error(self, error_object):
        if not isinstance(error_object, LDRNonFatal) and not isinstance(error_object,LDRFatal):
            raise Exception("bad error information being passed")
        else:
            self.errors.append(error_object)

    def add_request(self, request):
        if isinstance(request, Request):
            self.requests.append(request)
        else:
            return TypeError("must pass an instance of Request class")

    def get_errors(self):
        return self.errors

    def get_status(self):
        return self._status

    def set_output_passed(self):
        if not self._status:
            self._status = True
        return self._status

    def get_data(self):
        if self.data:
            return self.data
        else:
            return False

    def get_requests(self):
        return self.requests

    def add_data(self, data_object):
        if self.get_data():
            return False
        elif  type(data_object).__name__.lower() == self._type_string:
            self.data = data_object
            return True
        else:
            return False
