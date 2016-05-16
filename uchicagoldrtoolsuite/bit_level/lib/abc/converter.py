from abc import ABCMeta, abstractmethod

from pypremis.lib import PremisRecord

class Converter(metaclass=ABCMeta):

    _claimed_mimes = []

    def __init__(self, target_path, premis_path, working_dir=None, timeout=None):

        self._target_path = None
        self._target_premis_path = None
        self._target_premis = None
        self._working_dir = None
        self._timeout = None

        self.set_target_path(target_path)
        self.set_target_premis_path(premis_path)
        self.set_target_premis(PremisRecord(frompath=premis_path))
        if working_dir is None:
            self.set_working_dir(dirname(self.target_path))
        else:
            self.set_working_dir(working_dir)
        self.set_timeout(timeout)

    def get_claimed_mimes(self):
        return self._claimed_mimes

    def get_target_path(self):
        return self._target_path

    def get_target_premis_path(self):
        return self._target_premis_path

    def get_target_premis(self):
        return self._target_premis

    def get_working_dir(self):
        return self._working_dir

    def get_timeout(self):
        return self._timeout

    def set_target_path(self, x):
        self._target_path = x

    def set_target_premis_path(self, x):
        self._target_premis_path = x

    def set_target_premis(self, x):
        self._target_premis = x

    def set_working_dir(self, x):
        self._working_dir = x

    def set_timeout(self, x):
        self._timeout = x

    @abstractmethod
    def convert(self):
        pass

    claimed_mimes = property(get_claimed_mimes)
    target_path = property(get_target_path, set_target_path)
    target_premis_path = property(get_target_premis_path, set_target_premis_path)
    target_premis = property(get_target_premis, set_target_premis)
    working_dir = property(get_working_dir, set_working_dir)
    timeout = property(get_timeout, set_timeout)
