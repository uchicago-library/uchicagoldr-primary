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

    The other attributes functions return a NotImplementedError because
    they do not make sense to expect in an external source.
    """
    def __init__(self, orig, root=None):
        """
        spawn an ExternalFileSystemMaterialSuitePackager with the info it needs
        to package a file as a MaterialSuite

        __Args__

        1. orig (str): The path to the file

        __KWArgs__

        * root (str): A root for the provided path
        """
        super().__init__()
        self.orig = orig
        self.root = root

    def get_content(self):
        """
        Minimally turn a path into and LDRPath
        """
        return LDRPath(self.orig, root=self.root)

    def get_premis(self):
        raise NotImplementedError()

    def get_techmd_list(self):
        raise NotImplementedError()

    def get_presform_list(self):
        raise NotImplementedError()
