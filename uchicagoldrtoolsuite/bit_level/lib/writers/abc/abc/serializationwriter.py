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


class SerializationWriter(metaclass=ABCMeta):
    """
    ABC for all Serialization Writers

    assures the .write() method
    """
    @abstractmethod
    @log_aware(log)
    def __init__(self, struct, root, eq_detect="bytes"):
        log.debug("Entering the ABC init")
        self._struct = None
        self._root = None
        self._eq_detect = "bytes"
        self._implementation = None
        self.set_struct(struct)
        self.set_root(root)
        self.set_eq_detect(eq_detect)
        log.debug("Exiting the ABC init")

    @abstractmethod
    @log_aware(log)
    def write(self):
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
    def set_root(self, root):
        self._root = root

    @log_aware(log)
    def get_eq_detect(self):
        return self._eq_detect

    @log_aware(log)
    def set_eq_detect(self, x):
        self._eq_detect = x

    struct = property(get_struct, set_struct)
    root = property(get_root, set_root)
    eq_detect = property(get_eq_detect, set_eq_detect)
    implementation = property(get_implementation, set_implementation)
