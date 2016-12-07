from logging import getLogger
from pathlib import Path
from uuid import uuid4

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success, makedirs
from .abc.stageserializationwriter import StageSerializationWriter
from .filesystemmaterialsuitewriter import FileSystemMaterialSuiteWriter
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier


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
    def __init__(self, aStructure, aRoot,
                 materialsuite_serializer=FileSystemMaterialSuiteWriter,
                 eq_detect="bytes", materialsuite_serializer_kwargs={},
                 encapsulation="srf"):
        """
        Create a new FileSystemStageWriter instance

        __Args__

        1. aStructure (Stage): The structure to write
        2. aRoot (str): The path to a staging environment

        __KWArgs__

        * eq_detect (str): The equality metric to use during serialization
        """
        log_init_attempt(self, log, locals())
        super().__init__(
            aStructure, aRoot, materialsuite_serializer, eq_detect=eq_detect,
            materialsuite_serializer_kwargs=materialsuite_serializer_kwargs
        )
        self.encapsulation = encapsulation
        if 'encapsulation' not in self.materialsuite_serializer_kwargs.keys():
            self.materialsuite_serializer_kwargs['encapsulation'] = \
                self.encapsulation
        self.stage_root = Path(self.root, self.struct.identifier)
        self.set_implementation('filesystem (pairtree)')
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
            materialsuite_serializer = self.materialsuite_serializer(
                x, str(Path(self.stage_root, 'pairtree_root')),
                **self.materialsuite_serializer_kwargs)
            materialsuite_serializer.write()
        log.info("Stage written")

    @log_aware(log)
    def set_root(self, x):
        if not isinstance(x, str):
            raise TypeError(
                "{} is a {}, not a str!".format(
                    str(x), str(type(x))
                )
            )
        self._root = x
