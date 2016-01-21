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