from abc import ABCMeta, abstractmethod
from logging import getLogger

from uchicagoldrtoolsuite import log_aware


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago,edu tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class Packager(metaclass=ABCMeta):
    """
    ABC for packagers - the workhorses of readers which utilize internal
    reader information in addition to knowledge of a serialization in order
    to construct substructures in a larger structure
    """

    _struct = None
    _implementation = None

    @abstractmethod
    def __init__(self):
        pass

    @log_aware(log)
    def set_struct(self, value):
        self._struct = value

    @log_aware(log)
    def get_struct(self):
        return self._struct

    @log_aware(log)
    def set_implementation(self, value):
        return self._implementation

    @log_aware(log)
    def get_implementation(self, value):
        return self._implementation

    @abstractmethod
    def package(self):
        pass

    struct = property(get_struct, set_struct)
    implementation = property(get_implementation, set_implementation)
