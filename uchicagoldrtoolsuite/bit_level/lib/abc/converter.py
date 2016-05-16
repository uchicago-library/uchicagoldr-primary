from abc import ABCMeta, abstractmethod

from pypremis.lib import PremisRecord

class Converter(metaclass=ABCMeta):

    _claimed_mimes = []

    def __init__(self, target_path, premis_path, working_dir=None):
        self.target_path = target_path
        self.target_premis = PremisRecord(frompath=premis_path)
        if working_dir is None:
            self.working_dir = dirname(self.target_path)
        else:
            self.working_dir = working_dir

    def get_claimed_mimes(self):
        return self._claimed_mimes

    @abstractmethod
    def convert(self):
        pass

    claimed_mimes = property(get_claimed_mimes)
