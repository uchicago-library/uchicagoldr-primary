from os import makedirs as _makedirs
from logging import getLogger
from pathlib import Path
from uuid import uuid4

from pypairtree.utils import identifier_to_path

from uchicagoldrtoolsuite import log_aware
from .abc.stageserializationwriter import StageSerializationWriter
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.ldritemoperations import hash_ldritem
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, log_init_success


log = getLogger(__name__)


@log_aware(log)
def makedirs(x):
    """
    wrap makedirs, so it doesn't freak out if the dir is already there
    """
    _makedirs(x, exist_ok=True)


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
        required_dirs = []
        for x in ['admin', 'segments']:
            required_dirs.append(Path(self.stage_root, x))

        for x in ['accessionrecords', 'adminnotes', 'legalnotes']:
            required_dirs.append(Path(self.stage_root, 'admin', x))

        for x in required_dirs:
            if x.exists():
                if not x.is_dir():
                    raise RuntimeError("Stage writer can't clobber a file " +
                                       "where a directory should be! " +
                                       "{}".format(str(x)))
                log.info('{} exists, skipping creation'.format(str(x)))
            makedirs(str(x))

    @log_aware(log)
    def _write_accessionrecords(self):
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
        self._build_skeleton()
        self._write_accessionrecords()
        self._write_adminnotes()
        self._write_legalnotes()
        for x in self.struct.segment_list:
            ptfssw = FileSystemSegmentWriter(
                x, str(Path(self.stage_root, 'segments')),
                eq_detect=self.eq_detect
            )
            ptfssw.write()


class FileSystemSegmentWriter(object):
    """
    A writer for the pairtree based file system segment serialization

    Converters the structure and contained bytestreams into files/dirs
    on disk
    """
    @log_aware(log)
    def __init__(self, aStructure, aRoot, eq_detect="bytes"):
        """
        Create a new FileSystemSegmentWriter

        __Args__

        1. aStructure (Segment): The structure to serialize
        2. aRoot (str): The path to the segment root dir

        __KWArgs__

        * eq_detect (str): The equality metric to use during serialization
        """
        log_init_attempt(self, log, locals())
        self.struct = aStructure
        self.segment_root = Path(aRoot, self.struct.identifier)
        self.eq_detect = eq_detect
        log_init_success(self, log)

    @log_aware(log)
    def _write_skeleton(self):
        materialsuites_root = self.segment_root
        makedirs(str(materialsuites_root))

    @log_aware(log)
    def write(self):
        """
        Serialize the segment to the provided location
        """
        self._write_skeleton()
        for x in self.struct.materialsuite_list:
            ptfsmsw = FileSystemMaterialSuiteWriter(
                x,
                str(self.segment_root),
                eq_detect=self.eq_detect
            )
            ptfsmsw.write()


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
        makedirs(str(Path(self.materialsuite_root, 'TECHMD')))

    @log_aware(log)
    def write(self):
        """
        Serialize the material suite to the provided location
        """
        self._write_skeleton()
        target_content_path = Path(self.materialsuite_root, 'content.file')
        target_content_item = LDRPath(str(target_content_path))
        target_premis_path = Path(self.materialsuite_root, 'premis.xml')
        target_premis_item = LDRPath(str(target_premis_path))

        copiers = []

        copiers.append(LDRItemCopier(self.struct.premis, target_premis_item,
                                     clobber=True))

        if self.struct.content is not None:
            copiers.append(LDRItemCopier(self.struct.content, target_content_item,
                                         clobber=True))

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

        for x in copiers:
            cr = x.copy()
            if not cr['src_eqs_dst']:
                raise ValueError()
