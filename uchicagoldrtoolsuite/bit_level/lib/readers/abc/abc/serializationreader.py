from abc import ABCMeta, abstractmethod
from logging import getLogger

from uchicagoldrtoolsuite import log_aware


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class SerializationReader(metaclass=ABCMeta):
    """
    ABC for all Serialization Readers.

    Assures implementation of .read()
    """

    _struct = None
    _implementation = None

    @abstractmethod
    def read(self):
        pass

    @log_aware(log)
    def set_struct(self, struct):
        self._struct = struct

    @log_aware(log)
    def get_struct(self):
        return self._struct

    @log_aware(log)
    def set_implementation(self, implementation):
        self._implementation = implementation

    @log_aware(log)
    def get_implementation(self):
        return self._implementation

    struct = property(get_struct, set_struct)
    implementation = property(get_implementation, set_implementation)
