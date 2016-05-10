from .abc.materialsuitepackager import MaterialSuitePackager
from .ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ExternalFileSystemMaterialSuitePackager(MaterialSuitePackager):
    """
    Takes an (optionally rooted) path and places it into the content
    attribute of a MaterialSuite
    """
    def __init__(self, orig, root=None):
        super().__init__()
        self.orig = orig
        self.root = root

    def get_content(self):
        return LDRPath(self.orig, root=self.root)

    def get_premis(self):
        raise NotImplementedError()

    def get_techmd_list(self):
        raise NotImplementedError()

    def get_presform_list(self):
        raise NotImplementedError()
