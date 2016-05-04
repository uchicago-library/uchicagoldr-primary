from abc import abstractmethod

from .abc.packager import Packager


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class MaterialSuitePackager(Packager):
    """
    ABC for all MaterialSuitePackagers

    mandates:
        * .get_premis()
        * .get_techmd()
        * .get_presform()
    """
    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod
    def get_techmd(self):
        pass

    @abstractmethod
    def get_presform(self):
        pass
