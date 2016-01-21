
from uchicagoldrconfig.LDRConfiguration import LDRConfiguration

config = LDRConfiguration()

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

class Request(object):
    def __init__(self):
        pass

class InputRequestType(Request):
    type = None
    validate_function = None

    def __init__(self, vtype):
        self.type = vtype

    def validate_function(self):
        return True

    def validate(self):
        return isinstance(self.value, self.type) and self.validate_function()

class ChooseBetween(Request):
    choices = []
    valid = None

    def __init__(self, options):
        self.choices = options

    def validate(value):
        if value in choices:
            return True
        else:
            return False

class TrueOrFalse(Request):
    valid = None
    condition = False

    def __init__(self, condition):
        self.condition = condition

    def validate(value):
        if bool(value) == condition:
            return True
        else:
            return False

class ConfirmRequest(Request):
    valid = None
    value = None
    required = 'Y'

    def __init__(self, value):
        self.value = value

    def validate(self):
        if self.value == required:
            return True
        else:
            return False

class Output(object):
    requests = []
    error = None
    data  = None

    def __init__(self, type_string=None, status=None):
        if type_string is None:
            type_string = 'nonetype'
        if type_string in config['outputinformation']['valid_types']
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
        if isinstance(requet, Request):
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
        if self.type != None and data_object.__name__.lower() == self.type:
            self.data = data_object
            return 0
        else:
            return -1

    def display(self, record_format):
        if record_format in config['output_information']['valid_formats']:
            command = 'to_'+record_format
            return getattr(self.data.get_data(),command)()

