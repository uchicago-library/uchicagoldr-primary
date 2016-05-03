from abc import abstractmethod
from .abc.packager import Packager


class MaterialSuitePackager(Packager):
    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod
    def get_techmd(self):
        pass

    @abstractmethod
    def get_presform(self):
        pass