"""
The Stager class should be used in applications that need to create
staging directories
"""
from collections import namedtuple
from typing import NamedTuple
from treelib import Tree
from uchicagoldr.fileprocessor import FileProcessor
from uchicagoldr.rolevalidatorfactory import RoleValidatorFactory

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
                                                             for member in data.fields)))
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

