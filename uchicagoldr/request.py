from os.path import isabs
from os.path import isfile
from os.path import isdir
from re import match

from collections import Iterable

from uchicagoldr.error import LDRFatal, LDRNonFatal


class Request(object):
    def __init__(self, fall_through_error, validator=None, prompt=None):
        if validator is not None:
            self.validator = validator
        else:
            self.validator = self._dummy_validator

        self.prompt = prompt
        self.set_fall_through_error(fall_through_error)

    def _validator(self, response):
        return True

    def validate(self, response):
        return self.validator(response)

    def get_fall_through_error(self):
        return self.fall_through_error

    def set_fall_through_error(self, fall_through_error):
        if not isinstance(fall_through_error, LDRFatal) and \
                not isinstance(fall_through_error, LDRNonFatal):
            raise TypeError
        self.fall_through_error = fall_through_error


class InputType(Request):
    def __init__(self, fte, vtype, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Please supply a value of type: {}".format(str(vtype))
        Request.__init__(self, fte, validator, prompt=prompt)
        self.expected_type = vtype

    def _validator(self, response):
        return isinstance(response, self.expected_type)


class ChooseBetween(Request):
    def __init__(self, fte, options, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Please make a single selection from the choices."
        Request.__init__(self, fte, validator, prompt=prompt)
        self.choices = options

    def _validator(self, response):
        if response in self.choices:
            return True
        else:
            return False


class ChooseMultiple(Request):
    def __init__(self, fte, options, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Please indicate a selection from the choices."
        Request.__init__(self, fte, validator, prompt=prompt)
        self.choices = options

    def _validator(self, response):
        for entry in response:
            if entry not in self.choices:
                return False
        return True


class TrueOrFalse(Request):
    def __init__(self, fte, statement, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Please indicate whether the statement is true or false."
        Request.__init__(self, fte, validator, prompt=prompt)
        self.statement = statement

    def _validator(self, response):
        return isinstance(bool, response)


class Confirm(Request):
    def __init__(self, fte, value, validator=None, prompt=None):
        if validator is None:
            validator = self._validator
        if prompt is None:
            prompt = "Are you sure?"
        Request.__init__(self, fte, validator, prompt=prompt)
        self.value = value

    def _validator(self, response):
        return isinstance(bool, response)


class ProvideNewItemsInstance(InputType):
    def __init__(self, fte):
        self.prompt = "The items you provided were not a list or " + \
            "generator. Please supply a new list or generator of items."
        InputType.__init__(self, fte, Iterable, validator=self._validator,
                           prompt=self.prompt)

    def _validator(self, response):
        return isinstance(response, list) or \
            str(type(response)) == "<class 'generator'>"


class ProvideNewItemInstance(InputType):
    def __init__(self, fte):
        self.prompt = "The object you provided was not a valid item " + \
            "instance. Please supply a valid item instance."
        InputType.__init__(self, fte, Item, prompt=self.prompt)


class ProvideNewAccessionItemInstance(InputType):
    def __init__(self, fte):
        self.prompt = "The object you provided was not a valid accession " + \
            "item instance. Please supply a valid accession item instance."
        InputType.__init__(self, fte, AccessionItem, prompt=self.prompt)


class ProvideNewIndex(InputType):
    def __init__(self, fte, list_len):
        self.list_len = list_len
        self.prompt = "Please provide a new index. " + \
            "The list length is {}".format(str(self.list_len))
        InputType.__init__(self, fte, int, validator=self._validator,
                           prompt=self.prompt)

    def _validator(self, response):
        return bool(response < self.list_len)


class ProvideAbsolutePath(InputType):
    def __init__(self, fte):
        self.prompt = "The path you provided was not absolute. Please " + \
            "provide an absolute path."
        InputType.__init__(self, fte, str, validator=self._validator,
                           prompt=self.prompt)

    def _validator(self, response):
        return isinstance(response, str) and isabs(response)


class ProvideNewFilePath(ProvideAbsolutePath):
    def __init__(self, fte):
        self.prompt = "The path you provided was not absolute or did not " + \
            "point to a file on disk. Please provide a new filepath."
        InputType.__init__(self, fte, str, validator=self._validator,
                           prompt=self.prompt)

    def _validator(self, response):
        return isinstance(response, str) and isabs(response) and \
            isfile(response)


class ProvideNewIngestTargetPath(InputType):
    def __init__(self, fte):
        self.prompt = "The ingest target directory you specified is " + \
            "invalid. Targets must be directories specified by absolute " + \
            "paths."
        InputType.__init__(self, fte, str, validator=self._validator,
                           prompt=self.prompt)

    def _validator(self, response):
        return isinstance(response, str) and isdir(response)


class ProvideNewRoot(ProvideAbsolutePath):
    def __init__(self, fte):
        self.prompt = 'The root you specified is invalid. Please ' + \
            'provide a valid root path.'
        InputType.__init__(self, fte, str, validator=self._validator,
                           prompt=self.prompt)


class ProvideNewDataPath(ProvideAbsolutePath):
    def __init__(self, fte):
        self.prompt = 'The data path you specified is invalid. Please ' + \
            'provide a valid root path.'
        InputType.__init__(self, fte, str, validator=self._validator,
                           prompt=self.prompt)


class ProvideNewAdminPath(ProvideAbsolutePath):
    def __init__(self, fte):
        self.prompt = 'The admin path you specified is invalid. Please ' + \
            'provide a valid root path.'
        InputType.__init__(self, fte, str, validator=self._validator,
                           prompt=self.prompt)


class ProvideNewArk(InputType):
    def __init__(self, fte):
        self.prompt = "The ark you provided is not valid. " + \
            "Please provide a new one."
        InputType.__init__(self, fte, str, validator=self._validator,
                           prompt=self.prompt)

    def _validator(self, response):
        return isinstance(response, str) and match('^\w{13}$', response)


class MissingSourceDirectory(InputType):
    def __init__(self, fte):
        self.prompt = "the source directory you entered does not exist."
        InputType.__init__(self, fte, str, validator=self._ark_validation,
                           prompt=self.prompt)


class MissingDestinationDirectory(InputType):
    def __init__(self, fte):
        self.prompt = "the destination directory you entered does not exist."
        InputType.__init__(self, fte, str, validator=self._ark_validation,
                           prompt=self.prompt)


class CollissionProblem(InputType):
    def __init__(self, fte, collisions):
        self.prompt = "there was a collision between the " + \
            "following files".format(', '.join(collisions))
        InputType.__init__(self, fte, str, validator=self._ark_validation,
                           prompt=self.prompt)
