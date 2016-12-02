from logging import getLogger
from pathlib import Path
from uuid import uuid4

from pypairtree.utils import identifier_to_path

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success, makedirs
from .abc.stageserializationwriter import StageSerializationWriter
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


class FileSystemStageWriter(StageSerializationWriter):
    """
    A writer for the pairtree based file system stage serialization

    Converters the structure and contained bytestreams into files/dirs
    on disk
    """
    @log_aware(log)
    def __init__(self, aStructure, aRoot, eq_detect="bytes"):
        """
        Create a new FileSystemStageWriter instance

        __Args__

        1. aStructure (Stage): The structure to write
        2. aRoot (str): The path to a staging environment

        __KWArgs__

        * eq_detect (str): The equality metric to use during serialization
        """
        log_init_attempt(self, log, locals())
        super().__init__(aStructure)
        self.stage_env_path = Path(aRoot)
        self.stage_root = Path(self.stage_env_path, self.struct.identifier)
        self.set_implementation('pairtree filesystem')
        self.eq_detect = eq_detect
        log_init_success(self, log)

    @log_aware(log)
    def _build_skeleton(self):
        log.info("Creating required dirs/subdirs for the Stage serialization")
        required_dirs = []
        for x in ['admin', 'pairtree_root']:
            required_dirs.append(Path(self.stage_root, x))

        for x in ['accessionrecords', 'adminnotes', 'legalnotes']:
            required_dirs.append(Path(self.stage_root, 'admin', x))

        for x in required_dirs:
            if x.exists() and not x.is_dir():
                raise RuntimeError("Stage writer can't clobber a file " +
                                   "where a directory should be! " +
                                   "{}".format(str(x)))
            makedirs(str(x))

    @log_aware(log)
    def _write_accessionrecords(self):
        log.info("Writing accession records")
        for x in self.struct.accessionrecord_list:
            if x.item_name:
                item_name = x.item_name
            else:
                item_name = uuid4().hex
            target_path = Path(self.stage_root, 'admin',
                               'accessionrecords', item_name)
            target_item = LDRPath(str(target_path))
            copier = LDRItemCopier(x, target_item, eq_detect=self.eq_detect)
            cr = copier.copy()
            if not cr['src_eqs_dst'] and \
                    not cr['dst_existed'] and \
                    not cr['clobbered_dst']:
                raise ValueError("{}".format(str(cr)))

    @log_aware(log)
    def _write_adminnotes(self):
        log.info("Writing adminnotes")
        for x in self.struct.adminnote_list:
            if x.item_name:
                item_name = x.item_name
            else:
                item_name = uuid4().hex
            target_path = Path(self.stage_root, 'admin',
                               'adminnotes', item_name)
            target_item = LDRPath(str(target_path))
            copier = LDRItemCopier(x, target_item, eq_detect=self.eq_detect)
            cr = copier.copy()
            if not cr['src_eqs_dst'] and \
                    not cr['dst_existed'] and \
                    not cr['clobbered_dst']:
                raise ValueError("{}".format(str(cr)))

    @log_aware(log)
    def _write_legalnotes(self):
        log.info("Writing legalnotes")
        for x in self.struct.legalnote_list:
            if x.item_name:
                item_name = x.item_name
            else:
                item_name = uuid4().hex
            target_path = Path(self.stage_root, 'admin',
                               'legalnotes', item_name)
            target_item = LDRPath(str(target_path))
            copier = LDRItemCopier(x, target_item, eq_detect=self.eq_detect)
            cr = copier.copy()
            if not cr['src_eqs_dst'] and \
                    not cr['dst_existed'] and \
                    not cr['clobbered_dst']:
                raise ValueError("{}".format(str(cr)))

    @log_aware(log)
    def write(self):
        """
        Serialize the stage to the provided location
        """
        log.info("Writing stage")
        self._build_skeleton()
        self._write_accessionrecords()
        self._write_adminnotes()
        self._write_legalnotes()
        log.debug("Delegating segment writes to FileSystemSegmentWriter...")
        for x in self.struct.materialsuite_list:
            materialsuite_serializer = FileSystemMaterialSuiteWriter(
                x, str(Path(self.stage_root, 'pairtree_root')),
                eq_detect=self.eq_detect)
            materialsuite_serializer.write()
        log.info("Stage written")


class FileSystemMaterialSuiteWriter(object):
    """
    A writer for the pairtree based file system materialsuite serialization

    Converters the structure and contained bytestreams into files/dirs
    on disk
    """
    @log_aware(log)
    def __init__(self, aStructure, aRoot, eq_detect="bytes"):
        """
        Create a new FileSystemMaterialSuiteWriter

        __Args__

        1. aStructure (MaterialSuite): The structure to serialize
        2. aRoot (str): The path to the materialsuite root dir

        __KWArgs__

        * eq_detect (str): The equality metric to use during serialization
        """
        log_init_attempt(self, log, locals())
        self.struct = aStructure
        self.materialsuite_root = Path(
            identifier_to_path(self.struct.identifier, root=aRoot),
            "srf"
        )
        self.eq_detect = eq_detect
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

        copiers = []

        copiers.append(LDRItemCopier(self.struct.premis, target_premis_item,
                                     clobber=True))

        if self.struct.content is not None:
            copiers.append(LDRItemCopier(self.struct.content,
                                         target_content_item,
                                         clobber=True))

        log.debug("Computing techmd file names")
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
            copiers.append(LDRItemCopier(x, target_techmd_item, clobber=True))

        log.debug("Copying MaterialSuite bytestreams to disk")
        for x in copiers:
            cr = x.copy()
            if not cr['src_eqs_dst']:
                raise ValueError()
        log.info("MaterialSuite written")
