"""
The FileProcessor class should be used
"""
from collections import namedtuple
from os import stat
from os.path import join
from typing import NamedTuple
from magic import Magic
from uchicagoldr.absolutefilepathtree import AbsoluteFilePathTree
from uchicagoldr.rolevalidatorfactory import RoleValidatorFactory
from uchicagoldr.convenience import sane_hash
from uchicagoldr.destinationfactory import DestinationFactory
from uchicagoldr.filelister import FileLister

class FileProcessor(object):
    """A class for processing files from one stage of the archiving process to the next
    """
    def __init__(self, path: str, validation_type: str,
                 directory_data:\
                 NamedTuple("DirectoryInfo",
                            [('prefix', str), ('src_root', str), ('kind', str),
                             ('group_name', str), ('resume', int),
                             ('dest_root', str), ('directory_id', str),
                             ('directory_type', str)])):
        self.path = path
        self.tree = AbsoluteFilePathTree(path)

        self.files = self._find_files()
        self.relevant_files = [namedtuple("filedataobject", "path mimetype size checksums type")
                               (a_file_path, Magic(mime=True).from_file(a_file_path),
                                stat(a_file_path).st_size,
                                [namedtuple('checksum', "type value")('md5',sane_hash('md5',a_file_path))],
                                'file')
                               for a_file_path in FileLister(self._find_files()).\
                               filter_files(directory_data)
        ]
        self.validator = RoleValidatorFactory(validation_type).build(directory_data)
        self.validation = self.validate_input()
        self.destination = DestinationFactory(directory_data.directory_type).build(directory_data)


    def _find_files(self) -> list:
        """find files that need to be processed
        """
        return self.tree.get_files()


    def get_processor_info_needed(self):
        """A method to retrieve the kind of information that the validator in
        question requires and to retrieve that information
        """
        needed_info = self.validator.get_info_needed()
        extra_info = {}
        for key, value in needed_info.items():
            if key == 'numfilesfound':
                answer = len(self.files)
                if isinstance(answer, value):
                    extra_info[key] = answer
        return extra_info


    def validate_input(self):
        """A method to return True/False whether the input to the fileprocessor is true
        """
        addl_info = self.get_processor_info_needed()
        return self.validator.test(addl_info)


    def explain_validation_result(self):
        """A method to get an explanation for the validity/invalidity of the input
        """
        addl_info = self.get_processor_info_needed()
        category, answer = self.validator.verbose_test(addl_info)
        return namedtuple("answer", "category message")(category, answer)


    def move(self):
        """A method to move files from source to destination
        """
        if self.validation:
            nodes = self.tree.get_nodes()
            directory_nodes = [namedtuple("filepath", "type path")("directory", x)
                               for x in self.relevant_files if x.path not in nodes]
            file_nodes = [namedtuple("filepath", "type path")("file", x)
                          for x in self.relevant_files]
            
            self.destination.create()
            for n_directory in directory_nodes:
                self.destination.take_location(n_directory)
            for n_file in file_nodes:
                self.destination.take_location(n_file)
            return "{} has been moved to {}".format(self.path,
                                                    join(self.destination.destination_root,
                                                         self.destination.stage_id))
        else:
            return self.explain_validation_result()
