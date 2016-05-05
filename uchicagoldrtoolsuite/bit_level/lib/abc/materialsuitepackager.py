from abc import abstractmethod, ABCMeta

from .abc.packager import Packager
from ..materialsuite import MaterialSuite


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
        # .get_original()
        * .get_premis()
        * .get_techmd()
        * .get_presform()

    all of which should return iters of LDRItem subclasses
    if an implementation doesn't implement any of these by choice it should
    raise a NotImplementedError. The default .package() implementation
    simply eats these.
    """
    @abstractmethod
    def __init__(self, ldritem):
        self.set_struct(MaterialSuite())
        self.get_struct().add_original(ldritem)

    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod
    def get_techmd(self):
        pass

    @abstractmethod
    def get_presform(self):
        pass

    def package(self):
        """
        default package implementation
        """
        ms = self.get_struct()
        try:
            ms.set_premis_list(self.get_premis())
        except NotImplementedError:
            pass
        try:
            ms.set_presform_list(self.get_presform())
        except NotImplementedError:
            pass
        try:
            ms.set_technicalmetadata_list(self.get_techmd())
        except NotImplementedError:
            pass
        return ms
