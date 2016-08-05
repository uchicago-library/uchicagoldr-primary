from json import dumps

from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from ..readers.abc.materialsuitepackager import MaterialSuitePackager
from ..ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


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
        log.debug("ExternalFileSystemMaterialSuitePackager spawned. {}".format(
            dumps({'orig': orig, 'root': root})))
        super().__init__()
        self.orig = orig
        self.root = root

    def get_content(self):
        """
        Minimally turn a path into and LDRPath
        """
        log.debug("ExternalFileSystemMaterialSuitePackager retrieving " +
                  "content. {}".format(
                      dumps({'orig': self.orig, 'root': self.root})))
        return LDRPath(self.orig, root=self.root)

    def get_premis(self):
        raise NotImplementedError()

    def get_techmd_list(self):
        raise NotImplementedError()

    def get_presform_list(self):
        raise NotImplementedError()
