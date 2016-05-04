from abc import abstractmethod, ABCMeta

from .abc.packager import Packager
from .materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class MaterialSuitePackager(Packager, metaclass=ABCMeta):
    """
    ABC for all MaterialSuitePackagers

    mandates:
        * .get_premis()
        * .get_techmd()
        * .get_presform()
    """
    @abstractmethod
    def __init__(self):
        self.set_struct(MaterialSuite)

    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod
    def get_techmd(self):
        pass

    @abstractmethod
    def get_presform(self):
        pass
