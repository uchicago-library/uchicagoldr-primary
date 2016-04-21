from abc import abstractmethod
from .packager import Packager

class MaterialSuitePackager(Packager):

    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod
    def get_techmod(self):
        pass

    @abstractmethod
    def get_presform(self):
        pass
