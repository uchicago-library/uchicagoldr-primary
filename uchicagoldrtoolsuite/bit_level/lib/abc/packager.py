from abc import ABCMeta, abstractmethod, abstractproperty


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Packager(metaclass=ABCMeta):
    def set_struct(self, value):
        self._struct = value

    def get_struct(self):
        return self._struct

    def set_type(self, value):
        self._struct_type = value

    def get_type(self):
        return self._struct_type

    def set_implementation(self, value):
        return self._implementation

    def get_implementation(self, value):
        return self._implementation

    @abstractmethod
    def package(self):
        pass

    struct = abstractproperty(set_struct, get_struct)
    struct_type = abstractproperty(set_type, get_type)
    implementation = abstractproperty(set_implementation, get_implementation)
