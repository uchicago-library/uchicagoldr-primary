"""
The Stager class should be used in applications that need to create
staging directories
"""
from collections import namedtuple
from typing import NamedTuple
from treelib import Tree
from fileprocessor import FileProcessor
from rolevalidatorfactory import RoleValidatorFactory
from abc.validator import Validator


class NewStager(object):
    """NewStager is a concrete class intended to be used in application code.
    """

    def __init__(self, directory: str,
                 data: NamedTuple('DirectoryInfo',
                                  [('prefix', str), ('src_root', str),
                                   ('stage_id', str), ('dest_root', str),
                                   ('numfiles', int)])):
        self._processor = FileProcessor(directory)
        rolevalidatordata = namedtuple("info", "data")(dict(((member,
                                                              getattr(data,
                                                                      member))\
                                                             for member in data._fields)))
        info = namedtuple("info", "data")(rolevalidatordata)
        self.validator = RoleValidatorFactory('stager').build(info)


    def _get_snapshot_of_tree(self) -> NamedTuple("Snapshot", [('data', Tree)]):
        """A function to get a representation of the data in FileProcessor at
        for passage to a third party class (re: Valiadtor)
        """
        return namedtuple("Snapshot", "data")(self._processor.snapshot_tree())

    def validate(self) -> bool:
        """A method to return whether or not the input passed to the Stager is valid
        """
        return self.validator.test(self._get_snapshot_of_tree())

    def explain_results(self) -> NamedTuple("problem",
                                            [("category", str), ("message", str)]):
        """A method for returning to the user an explanation of why the input failed to validate.
        """
        result = self.validator.verbose_test(self._get_snapshot_of_tree())
        return namedtuple("problem", "category message")("fatal", result)

    def get_processor(self):
        """method to get the value in the processor member
        """
        return "this is a private data member"


    def set_processor(self, value):
        """method to type check setting the value of the processor data member
        """
        if isinstance(value, FileProcessor) != True:
            raise ValueError("processor data member must have a value " + \
                             "that is an instance of the FileProcessor class")
        self._processor = value


    def get_validator(self):
        """method to get the value of the validator data member
        """
        return self.validator

    def set_validator(self, value):
        """method to to type check setting the value of the validator data member
        """
        if isinstance(value, Validator) != True:
            raise ValueError("validator data member must have a vlaue " + \
                             "that is an instance of the Validator class")
        self.validator = value


    _processor = property(get_processor, set_processor)
    validator = property(get_validator, set_validator)
