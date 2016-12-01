from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import recursive_scandir, \
    log_init_attempt, log_init_success
from ..readers.abc.segmentpackager import SegmentPackager
from ..structures.segment import Segment
from .externalfilesystemmaterialsuitepackager import\
    ExternalFileSystemMaterialSuitePackager


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class ExternalFileSystemSegmentPackager(SegmentPackager):
    @log_aware(log)
    def __init__(self, path, label_text, label_number, root=None,
                 filter_pattern=None):
        """
        instantiate a new ExternalFileSystemSegmentPackager with all the
        information that it will need to package the contents of an external
        directory as a segment to be inserted into an existing Stage.

        __Args__

        1. path (str): The path to the external directory whose contents
            are going to be packaged in the segment
        2. label_text (str): The label for the first part of the segments id
        3. label_number (int): The number for the second part of the segments
            id

        __KWArgs__

        * root (str): A path root to remove from the item information, by
            default this will be the containing directory of the specified
            directory
        """
        log_init_attempt(self, log, locals())
        super().__init__()
        self.path = path
        self.set_implementation("file system")
        self.set_msuite_packager(ExternalFileSystemMaterialSuitePackager)
        self.set_id_prefix(label_text)
        self.set_id_num(label_number)
        self.set_struct(Segment(self.get_id_prefix(), int(self.get_id_num())))
        self.root = root
        self.filter_pattern = filter_pattern
        log_init_success(self, log)

    @log_aware(log)
    def package(self):
        """
        grab all the files out of the supplied path,
        coerce them into MaterialSuites, add those materialsuites to a segment
        and return the segment.
        """
        log.info("Beginning segment packaging for {}".format(
            self.struct.identifier)
        )
        for x in recursive_scandir(self.path):
            if not x.is_file():
                continue
            # TODO
            # Filter pattern should probably be reintroduced HERE, in a try
            # catch type re-encoding of the filename from bytes.
            log.debug("Instantiating MaterialSuite packagers and adding the" +
                      "results to the segment")
            self.struct.add_materialsuite(
                self.get_msuite_packager()(x.path, root=self.root).package()
            )
        return self.struct
