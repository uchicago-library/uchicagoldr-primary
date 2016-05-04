from abc import ABCMeta, abstractmethod


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class SerializationReader(metaclass=ABCMeta):
    """
    ABC for all Serialization Readers.

    Assures implementation of .read()
    """

    _struct = None
    _implementation = None

    @abstractmethod
    def read(self, aStructure, aString):
        pass

    def set_struct(self, struct):
        self._struct = struct

    def get_struct(self):
        return self._struct

    def set_implementation(self, implementation):
        self._implementation = implementation

    def get_implementation(self):
        return self._implementation

    property(get_struct, set_struct)
    property(get_implementation, set_implementation)
