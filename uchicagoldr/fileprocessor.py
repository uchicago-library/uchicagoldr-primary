"""
The FileProcessor class should be used
"""
from collections import namedtuple
from typing import Generic
from uchicagoldr.absolutefilepathtree import AbsoluteFilePathTree


class FileProcessor(object):
    """FileProcessor abstract class
    """
    class FileDataObject(object):
        """DataTransferObject for files found in self.tree
        """
        def __init__(self, filepath: str):
            self.path = filepath
            self.checksums = None
            self.mimetype = "None"
            self.size = 0

        def set_value(self, value: str, type_str: str, extra=None) -> None:
            """set a value to the right attribute
            """
            if type_str == 'mimetype':
                self.mimetype = value
            elif type_str == 'checksum':
                self.set_a_cheksum(vaue, extra=extra)
            elif type_str == 'size':
                self.size = value


        def get_size(self) -> str:
            """A method to get the value of the size data member
            """
            return self._size


        def set_size(self, value) -> None:
            """A method to set the value of the size data member
            """
            if not isinstance(value, int):
                raise ValueError("{} is not a integer".format(value))
            self._size = value


        def get_mimetype(self) -> str:
            """A method to get the value of the mimetype data member
            """
            return self._mimetype


        def set_mimetype(self, value) -> None:
            """A method to set the value of the mimetype data member
            """
            if not isinstance(value, str):
                raise ValueError("{} is not a string.".format(value))
            self._mimetype = value


        def get_checksums(self) -> str:
            """A method to get the value of the checksums data member
            """
            return "cannot access this data member directly: " +\
                "use the method get_a_checksum"


        def get_a_checksum(self, type_str: str) -> str:
            """A method to retrieve a specific type of checksum
            """
            print(x._checksums)
            if not isinstance(type_str, str):
                raise ValueError("must pass a string denoting the type of checksum you want to get")
            elif not type_str in ['md5', 'sha256']:
                raise ValueError("you are requesting a checksum that is not valid.")
            else:
                answer = [x for x in self.checksums if x.type == type_str][0]
                if answer:
                    return answer[0]
                else:
                    raise ValueError("You cannot request a checksum that has" +\
                                     "not been calculated yet")


        def set_checksums(self, value: str) -> None:
            return ""


        def set_a_checksum(self, value, extra="") -> None:
            """The real method to set a value in the checksums data member
            """
            print(x.checksums)
            if not isinstance(value, str):
                raise ValueError("{} is not a string".format(value))
            if extra not in ['sha', 'md5']:
                raise ValueError("can only accept 'sha' or 'md5' type checksums")
            if not getattr(self, 'checksums', None):
                self._checksums = [namedtuple("checksum", "type value")(extra,
                                                                       value)]
            elif [a_checksum for a_checksum in self.checksums if a_checksum.type == extra]:
                raise ValueError("you already saved a checksum of type {}".format(extra))
            else:
                self._checksums.append(namedtuple("checksum", "type value")(extra,
                                                                           value))


        def get_value(self, type_str: str) -> str:
            """get a value based on a type string entered as a parameter
            """
            if getattr(self, type_str, None):
                return getattr(self, type_str, None)
            else:
                raise ValueError("There is no attribute {}".format(type_str))


        size = property(get_size, set_size)
        mimetype = property(get_mimetype, set_mimetype)
        checksums = property(get_checksums, set_checksums)


    def __init__(self, path: str):
        self.tree = AbsoluteFilePathTree(path)
        self.files = [self.FileDataObject(a_file_path)
                      for a_file_path in self.tree.get_files()]

    def get_snapshot_of_a_tree(self):
        """a function to return the tree
        """
        return self.tree

    def calculate_checksums(self) -> None:
        """find checksums (md5 and sha256) for the files in self.files
        """
        checksums = self.tree.get_md5s()
        self._locate_path_in_a_dict(checksums, 'checksums', extra='md5')
        checksums_prime = self.tree.get_shas()
        self._locate_path_in_a_dict(checksums_prime, 'checksums', extra='sha256')


    def calculate_mimetypes(self) -> None:
        """find mimetypes for files in self.files
        """
        mimes = self.tree.get_mimes_from_magic_number()
        self._locate_path_in_a_dict(mimes, 'mimetype')


    def calculate_filesizes(self) -> None:
        """find file sizes for files in self.files
        """
        filesizes = self.tree.get_file_sizes()
        self._locate_path_in_a_dict(filesizes, 'size')


    def _locate_path_in_a_dict(self, a_dict: dict, type_str: str,
                               extra=None) -> None:
        def define_attribute_in_file(current_object: Generic(self.FileDataObject),
                                     value: str):
            """function to set a value on a matched FileDataObject
            """
            current_object.set_value(value, type_str, extra=extra)


        for a_file in self.files:
            value = a_dict.get(a_file.path)
            if not extra:
                define_attribute_in_file(a_file, value)
            else:
                define_attribute_in_file(a_file, value)
        return True

    def snapshot_tree(self):
        """a function to treturn a copy of the tree data
        """
        return self.tree.return_tree()

    def get_files(self):
        """A getter method for retrieving the value of the files data member
        """
        return self.files

    def set_files(self):
        """A setter method for setting the value of teh files data member
        """
        if not getattr(self.tree, None):
            raise ValueError("cannot get files without a complete tree")
        self.files = self.tree.get_files()

    def _find_files(self) -> list:
        """find files that need to be processed
        """
        if not self.files:
            self.files = self.tree.get_files()
        else:
            pass
        return self.files
