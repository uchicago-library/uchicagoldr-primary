from logging import getLogger
from pathlib import Path

from pypremis.lib import PremisRecord
from pypairtree.utils import identifier_to_path

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success, makedirs
from .abc.materialsuiteserializationwriter import \
    MaterialSuiteSerializationWriter
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.ldritemoperations import hash_ldritem


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class FileSystemMaterialSuiteWriter(MaterialSuiteSerializationWriter):
    """
    A writer for the pairtree based file system materialsuite serialization

    Converters the structure and contained bytestreams into files/dirs
    on disk
    """
    @log_aware(log)
    def __init__(self, aStructure, aRoot, eq_detect="bytes",
                 encapsulation="srf", premis_event=None,
                 update_content_location=False, clobber=True):
        """
        Create a new FileSystemMaterialSuiteWriter

        __Args__

        1. aStructure (MaterialSuite): The structure to serialize
        2. aRoot (str): The path to the materialsuite root dir

        __KWArgs__

        * eq_detect (str): The equality metric to use during serialization
        """
        log_init_attempt(self, log, locals())
        super().__init__(
            aStructure, aRoot, update_content_location=update_content_location,
            premis_event=premis_event
        )
        self.materialsuite_root = Path(
            identifier_to_path(self.struct.identifier, root=self.root),
            encapsulation
        )
        self.eq_detect = eq_detect
        self.set_implementation("filesystem (pairtree)")
        self.clobber = clobber
        log_init_success(self, log)

    @log_aware(log)
    def _write_skeleton(self):
        log.info("Writing required dirs/subdirs for a "
                 "MaterialSuite serialization")
        if self.materialsuite_root.exists() and \
                not self.materialsuite_root.is_dir():
            raise RuntimeError("MaterialSuite writer can't clobber a file " +
                               "where a directory should be! " +
                               "{}".format(str(self.materialsuite_root)))
        makedirs(str(Path(self.materialsuite_root, 'TECHMD')))

    @log_aware(log)
    def write(self):
        """
        Serialize the material suite to the provided location
        """
        log.info("Writing MaterialSuite")
        self._write_skeleton()
        log.debug("Constructing target paths")
        target_content_path = Path(self.materialsuite_root, 'content.file')
        target_content_item = LDRPath(str(target_content_path))
        target_premis_path = Path(self.materialsuite_root, 'premis.xml')
        target_premis_item = LDRPath(str(target_premis_path))

        premis_copier = LDRItemCopier(self.struct.premis, target_premis_item,
                                      clobber=self.clobber)
        content_copier = None
        if self.struct.content is not None:
            content_copier = LDRItemCopier(self.struct.content,
                                           target_content_item,
                                           clobber=self.clobber)

        log.debug("Computing techmd file names")
        techmd_copiers = []
        for x in self.struct.technicalmetadata_list:
            # Use a quick checksum as the file name, this should prevent
            # un-needed writing so long as the records don't change in between
            # reading and writing a stage where the TECHMD already exists.
            # It also keeps the names equivalent if a stage is moved
            # from one root to another.
            # So long as the file sizes stay small the overhead of computing
            # a quick checksum like adler should be negligible.
            h = hash_ldritem(x, algo="adler32")
            target_techmd_path = Path(self.materialsuite_root,
                                      'TECHMD', h)
            target_techmd_item = LDRPath(str(target_techmd_path))
            techmd_copiers.append(LDRItemCopier(x, target_techmd_item,
                                                clobber=self.clobber))

        log.debug("Copying MaterialSuite bytestreams to disk")
        content_cr = None
        for x in [premis_copier, content_copier] + techmd_copiers:
            if x is not None:
                cr = x.copy()
                if not cr['src_eqs_dst']:
                    raise ValueError()
                if x == content_copier:
                    content_cr = cr

        if self.premis_event_entry or self.update_content_location:
            premis = PremisRecord(frompath=str(target_premis_path))
            if self.update_content_location:
                self.content_location_update(premis, str(target_premis_path))
            if self.premis_event_entry:
                self.finalize_event(
                    premis, self.premis_event_entry,
                    eventOutcomeDetailNote=content_cr
                )
            premis.write_to_file(str(target_premis_path))

        log.info("MaterialSuite written")
