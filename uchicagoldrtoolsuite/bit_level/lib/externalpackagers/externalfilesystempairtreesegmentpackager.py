from .externalfilesystemsegmentpackager import ExternalFileSystemSegmentPackager
from .externalfilesystempairtreematerialsuitepackager import\
    ExternalFileSystemPairTreeMaterialSuitePackager
from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ExternalFileSystemPairTreeSegmentPackager(ExternalFileSystemSegmentPackager):
    def __init__(self, path, label_text, label_number, root=None,
                 filter_pattern=None):
        super().__init__(path, label_text, label_number, root=root, filter_pattern=filter_pattern)
        self.set_msuite_packager(ExternalFileSystemPairTreeMaterialSuitePackager)
