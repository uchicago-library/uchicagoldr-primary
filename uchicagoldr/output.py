
from uchicagoldrconfig.LDRConfiguration import LDRConfiguration
from uchicagoldr.request import Request

config = LDRConfiguration()

class Output(object):
    requests = []
    type_string = None
    status = None
    error = None
    data  = None

    def __init__(self, type_string=None, status=None):
        if not type_string:
            type_string = 'nonetype'
        elif typestring in config['outputinformation']['valid_types']:
            self.type = type_string
        else:
            self.type = None
        if status is None:
            self.status = False
        else:
            self.status = status
        self.data = None
        self.requests = []

    def add_error(self, error_object):
        if self.error != None:
            return Output(status=False)
        elif not isinstance(error_object, LDRError):
            return Output(status=False)
        else:
            self.error = error_object

    def add_request(self, request):
        if isinstance(request, Request):
            self.requests.append(request)
        else:
            return TypeError("must pass an instance of Request class")

    def get_error(self):
        if self.error != None:
            return "{0}: {1}".format(self.error.get_label(),
                                     self.error.get_message())
    def get_status(self):
        return self.status

    def set_status(self, new_status):
        assert(isinstance(new_status,bool))
        self.status = new_status

    def get_data(self):
        if self.data:
            return self.data
        else:
            return False

    def get_requests(self):
        if len(self.requests) > 0:
            return self.requests
        else:
            return False

    def add_data(self, data_object):
        if self.type_string != None and data_object.__name__.lower() == self.type_string:
            self.data = data_object
            return 0
        else:
            return -1

    def display(self, record_format):
        if record_format in config['output_information']['valid_formats']:
            command = 'to_'+record_format
            return getattr(self.data.get_data(),command)()

