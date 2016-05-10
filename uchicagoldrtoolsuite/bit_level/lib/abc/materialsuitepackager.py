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
    def __init__(self):
        self.set_struct(MaterialSuite())

    @abstractmethod
    def get_content(self):
        pass

    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod
    def get_techmd_list(self):
        pass

    @abstractmethod
    def get_presform_list(self):
        pass

    def package(self):
        """
        default package implementation
        """
        ms = self.get_struct()
        try:
            ms.set_content(self.get_content())
        except NotImplementedError:
            pass
        try:
            ms.set_premis(self.get_premis())
        except NotImplementedError:
            pass
        try:
            ms.set_presform_list(self.get_presform_list())
        except NotImplementedError:
            pass
        try:
            ms.set_technicalmetadata_list(self.get_techmd_list())
        except NotImplementedError:
            pass
        return ms
