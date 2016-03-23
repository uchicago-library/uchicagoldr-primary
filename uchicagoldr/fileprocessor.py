"""
The FileProcessor class should be used
"""
from typing import Callable
from uchicagoldr.absolutefilepathtree import AbsoluteFilePathTree


class FileProcessor(object):
    """FileProcessor abstract class
    """
    class FileDataObject(object):
        """DataTransferObject for files found in self.tree
        """
        def __init__(self, filepath: str):
            self.path = filepath
            self.mimetype = None
            self.size = 0
            self.checksum = None


        def set_value(self, value: str, type_str: str):
            """set a value to the right attribute
            """
            if type_str == 'mimetype':
                self.mimetype = value
            elif type_str == 'size':
                self.size = value


        def get_value(self, type_str: str) -> str:
            """get a value based on a type string entered as a parameter
            """
            if getattr(self, type_str, None):
                return getattr(self, type_str, None)
            else:
                raise ValueError("There is no attribute {}".format(type_str))


    def __init__(self, path: str):
        self.tree = AbsoluteFilePathTree(path)
        self.files = None


    def calculate_checksums(self) -> None:
        """find checksums (md5 and sha256) for the files in self.files
        """
        checksums = self.tree.get_md5s()
        checksums_prime = self.tree.get_shas()
        checksums.update(checksums_prime)
        self._locate_path_in_a_dict(checksums, 'checksum')


    def calculate_mimetypes(self) -> None:
        """find mimetypes for files in self.files
        """
        mimes = self.tree.get_mimes_from_magic_number()
        self._locate_path_in_a_dict(mimes, 'mimetype')


    def calculate_filesizes(self) -> None:
        """find file sizes for files in self.files
        """
        filesizes = self.tree.get_file_sizes()
        self._locate_path_in_a_dict(filesizes, 'filesize')


    def _locate_path_in_a_dict(self, a_dict: dict, type_str: str) -> None:
        def define_attribute_in_file(current_object: Callable(self.FileDataObject),
                                     value: str):
            """function to set a value on a matched FileDataObject
            """
            current_object.set_value(value, type_str)


        for a_file in self.files:
            value = a_dict.get(a_file.filepath)
            define_attribute_in_file(a_file, value)
            return value


    def _find_files(self) -> list:
        """find files that need to be processed
        """
        if not self.files:
            self.files = self.tree.get_files()
        else:
            pass
        return self.files
