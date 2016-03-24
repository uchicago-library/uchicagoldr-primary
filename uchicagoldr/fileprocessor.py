"""
The FileProcessor class should be used
"""
from collections import namedtuple
from os import stat
from typing import NamedTuple
from magic import Magic
from uchicagoldr.absolutefilepathtree import AbsoluteFilePathTree
from uchicagoldr.rolevalidatorfactory import RoleValidatorFactory
from uchicagoldr.convenience import sane_hash

class FileProcessor(object):
    """A class for processing files from one stage of the archiving process to the next
    """
    def __init__(self, path: str, validation_type: str,
                 directory_data:\
                 NamedTuple("DirectoryInfo",
                            [('prefix', str), ('src_root', str),
                             ('dest_root', str), ('stage_id', str)]
                 validation_data:\
                 NamedTuple('Rules',
                             ('numfiles', int)])):
        self.tree = AbsoluteFilePathTree(path)
        self.files = [namedtuple("filedataobject",
                                 "path mimetype size checksums")\
                      (a_file_path, Magic(mime=True).from_file(a_file_path),
                       stat(a_file_path).st_size,
                       [namedtuple("checksum",
                                   "type value")('md5',
                                                 sane_hash('md5',
                                                           a_file_path))])
                      for a_file_path in self._find_files()]
        self.validator = RoleValidatorFactory(validation_type).build(validation_data)
        self.validation = _self.validate_input()
        self.destination = DestinationFactory(directory_info.kind).build()


    def get_snapshot_of_a_tree(self):
        """a function to return the tree
        """
        return self.tree


    def _find_files(self) -> list:
        """find files that need to be processed
        """
        return self.tree.get_files()


    def _get_processor_info_needed(self):
        """A method to retrieve the kind of information that the validator in
        question requires and to retrieve that information
        """
        needed_info = validator.what_info_is_needed()
        extra_info = {}
        for key,value in needed_info.items():
            if key == 'numfilesfound':
                answer = len(self.files)
                if isinstance(answer, value):
                    extra_info[k] = answer
        return extra_info


    def _validate_input(self):
        """A method to return True/False whether the input to the fileprocessor is true
        """
        addl_info = self._get_processor_info_needed()
        return validator.test(addl_info)


    def is_it_valid(self):
        """A method to return the result of validating the input
        """
        return self.validation


    def explain_validaiton_result(self):
        """A method to get an explanation for the validity/invalidity of the input
        """
        addl_info = self._get_processor_info_needed()
        category, answer = validator.verbose_test(addl_info)
        return namedtuple("answer", "category message")(category, answer)


    def move(self):
        """A method to move files from source to destination
        """
        if self.validation:
            self.destination.create()
            for n_item in self.tree.all_nodes():
                self.destination.take_file(n_item)
        else:
            return explain_validation_result()
