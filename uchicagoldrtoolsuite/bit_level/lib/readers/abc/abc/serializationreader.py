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
    @abstractmethod
    @log_aware(log)
    def __init__(self, root, target_identifier):
        _struct = None
        _root = None
        _target_identifier = None
        _implementation = None
        self.root = root
        self.target_identifier = target_identifier

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

    @log_aware(log)
    def get_root(self):
        return self._root

    @log_aware(log)
    def set_root(self, x):
        self._root = x

    @log_aware(log)
    def get_target_identifier(self):
        return self._target_identifier

    @log_aware(log)
    def set_target_identifier(self, x):
        self._target_identifier = x

    struct = property(get_struct, set_struct)
    implementation = property(get_implementation, set_implementation)
    root = property(get_root, set_root)
    target_identifier = property(get_target_identifier, set_target_identifier)
