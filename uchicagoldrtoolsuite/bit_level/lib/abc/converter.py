from abc import ABCMeta, abstractmethod
from os.path import dirname

from pypremis.lib import PremisRecord

class Converter(metaclass=ABCMeta):

    _claimed_mimes = []

    def __init__(self, input_materialsuite, working_dir, timeout=None):

        self._source_materialsuite = None
        self._working_dir = None
        self._timeout = None

        self.set_source_materialsuite(input_materialsuite)
        self.set_working_dir(working_dir)
        self.set_timeout(timeout)

    def get_claimed_mimes(self):
        return self._claimed_mimes

    def get_source_materialsuite(self):
        return self._source_materialsuite

    def get_working_dir(self):
        return self._working_dir

    def get_timeout(self):
        return self._timeout

    def set_source_materialsuite(self, x):
        self._source_materialsuite = x

    def set_working_dir(self, x):
        self._working_dir = x

    def set_timeout(self, x):
        self._timeout = x

    @abstractmethod
    def convert(self):
        pass

    claimed_mimes = property(get_claimed_mimes)
    source_materialsuite = property(get_source_materialsuite, set_source_materialsuite)
    working_dir = property(get_working_dir, set_working_dir)
    timeout = property(get_timeout, set_timeout)
