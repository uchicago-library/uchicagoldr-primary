from .abc.materialsuitepackager import MaterialSuitePackager
from .materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemMaterialSuitePackager(MaterialSuitePackager):
    """
    Reads a file system MaterialSuite serialization and knows how to package
    material suites from the contents for inclusion in segment structures
    """
    def __init__(self):
        super().__init__()
        self.set_implementation('file system')

    def package(self, an_item):
        msuite = MaterialSuite(an_item)
        msuite.original.append(an_item)
        return msuite

    def get_techmd(self):
        pass

    def get_presform(self):
        pass

    def get_premis(self):
        pass
