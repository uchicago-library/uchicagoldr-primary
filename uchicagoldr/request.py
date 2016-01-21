class Request(object):
    def __init__(self, validator=None, prompt=None):
        if validator is not None:
            self.validator = validator
        else:
            self.validator = self._dummy_validator

        self.prompt = prompt

    def _dummy_validator(self, response):
        return True

    def validate(self, response):
        return self.validator(response)


class InputType(Request):
    def __init__(self, vtype, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Please supply a value of type: {}".format(str(vtype))
        Request.__init__(self, validator, prompt=prompt)
        self.expected_type = vtype

    def _validator(self, response):
        return isinstance(response, self.expected_type)


class ChooseBetween(Request):
    def __init__(self, options, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Please make a single selection from the choices."
        Request.__init__(self, validator, prompt=prompt)
        self.choices = options

    def _validator(self, response):
        if response in self.choices:
            return True
        else:
            return False


class ChooseMultiple(Request):
    def __init__(self, options, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Please indicate a selection from the choices."
        Request.__init__(self, validator, prompt=prompt)
        self.choices = options

    def _validator(self, response):
        for entry in response:
            if entry not in self.choices:
                return False
        return True


class TrueOrFalse(Request):
    def __init__(self, statement, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Please indicate whether the statement is true or false."
        Request.__init__(self, validator, prompt=prompt)
        self.statement = statement

    def _validator(self, response):
        return isinstance(bool, response)


class Confirm(Request):
    def __init__(self, value, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Are you sure?"
        Request.__init__(self, validator, prompt=prompt)
        self.value = value

    def _validator(self, response):
        return isinstance(bool, response)
