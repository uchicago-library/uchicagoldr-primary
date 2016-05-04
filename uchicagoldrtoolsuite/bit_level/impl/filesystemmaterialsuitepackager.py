from ..lib.materialsuitepackager import MaterialSuitePackager
from ..lib.materialsuite import MaterialSuite


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
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
        self.set_struct(MaterialSuite)
        self.set_implementation('directory')

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
