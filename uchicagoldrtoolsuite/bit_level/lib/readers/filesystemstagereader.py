from pathlib import Path
from logging import getLogger
from os import scandir

from pypairtree.utils import path_to_identifier, identifier_to_path

from uchicagoldrtoolsuite.core.lib.convenience import recursive_scandir
from uchicagoldrtoolsuite import log_aware
from .abc.stageserializationreader import StageSerializationReader
from .abc.segmentpackager import SegmentPackager
from .abc.materialsuitepackager import MaterialSuitePackager
from ..structures.segment import Segment
from ..ldritems.ldrpath import LDRPath
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, log_init_success


log = getLogger(__name__)


class FileSystemStageReader(StageSerializationReader):
    """
    The reader for pairtree based FileSystem stage structure serializations.
    Given the location of a stage reconstructs the stage structure from byte
    streams serialized as files on disk.
    """
    # TODO: Should this be changed to be more similar to the archive reader,
    # which accepts an environment path and an identifier rather than just a
    # single path? Probably. - BNB
    @log_aware(log)
    def __init__(self, path):
        """
        Create a new FileSystemStageReader

        __Args__

        1. path (str): The path to the stage on disk. The leaf component should
            be the stage identifier
        """
        log_init_attempt(self, log, locals())
        super().__init__()
        self.path = path
        self.struct.set_identifier(str(Path(path).parts[-1]))
        log_init_success(self, log)

    @log_aware(log)
    def assert_skeleton(self):
        accessionrecords_dir = Path(self.path, 'admin', 'accessionrecords')
        legalnotes_dir = Path(self.path, 'admin', 'legalnotes')
        adminnotes_dir = Path(self.path, 'admin', 'adminnotes')
        segments_dir = Path(self.path, 'segments')
        for x in [accessionrecords_dir, legalnotes_dir,
                  adminnotes_dir, segments_dir]:
            if not x.is_dir():
                log.debug("Failed assert_skeleton(), missing {}".format(str(x)))
                return False
        return True

    @log_aware(log)
    def read(self):
        """
        Reads the structure at the given location

        __Returns__

        * self.struct (Stage): The stage
        """
        # If there's not a valid stage skeleton on the file system here return a
        # blank staging structure. Whether or not this should "fail" silently or
        # raise an error might warrant inclusion as a kwarg/CLI flag?
        log.info("Reading stage")
        if not self.assert_skeleton():
            log.warn("No stage detected - assuming a blank stage")
            return self.struct

        accessionrecords_dir = Path(self.path, 'admin', 'accessionrecords')
        legalnotes_dir = Path(self.path, 'admin', 'legalnotes')
        adminnotes_dir = Path(self.path, 'admin', 'adminnotes')
        segments_dir = Path(self.path, 'segments')

        log.debug("Adding accession records")
        for x in [x.path for x in scandir(str(accessionrecords_dir))]:
            self.struct.add_accessionrecord(LDRPath(x))
        log.debug("Adding legalnotes")
        for x in [x.path for x in scandir(str(legalnotes_dir))]:
            self.struct.add_legalnote(LDRPath(x))
        log.debug("Adding adminnotes")
        for x in [x.path for x in scandir(str(adminnotes_dir))]:
            self.struct.add_adminnote(LDRPath(x))
        log.debug("Adding segments resulting from delegation to the " +
                  "FileSystemSegmentReader")
        for x in [x.path for x in scandir(str(segments_dir))]:
            self.struct.add_segment(
                FileSystemSegmentReader(
                    x,
                    str(Path(x).parts[-1]).split("-")[0],
                    str(Path(x).parts[-1]).split("-")[1]
                ).package()
            )
        log.info("Stage read")
        return self.struct


class FileSystemSegmentReader(SegmentPackager):
    """
    The packager for pairtree based segment serializations

    Given the path and identifier components of a Segment, package that segment
    up and return it
    """
    @log_aware(log)
    def __init__(self, path, label_text, label_number):
        """
        Create a new FileSystemSegmentReader

        __Args__

        1. path (str): The path the segment is located at
        2. label_text (str): The textual component of the segment label
        3. label_number (str/int): The numeric component of the segment label
        """
        super().__init__()
        self.path = path
        self.set_struct(Segment(label_text, int(label_number)))

    @log_aware(log)
    def _gather_identifiers(self):
        log.debug("Scanning filesystem to compute materialsuite identifiers")
        identifiers = []
        for f in recursive_scandir(self.path):
            if not f.is_file():
                continue
            f = f.path
            if not f.endswith("premis.xml"):
                continue
            rel_p = Path(f).relative_to(self.path)
            # remove the file and ecapsulation
            id_dir_path = Path(rel_p.parents[1])
            identifiers.append(path_to_identifier(id_dir_path))
        return identifiers

    @log_aware(log)
    def package(self):
        """
        Packages the structure at the given location

        __Returns__

        self.struct (Segment): The segment
        """
        log.info("Packaging Segment")
        for ident in self._gather_identifiers():
            log.debug("Adding result of delegation to " +
                      "FileSystemMaterialSuiteReader")
            self.struct.add_materialsuite(
                FileSystemMaterialSuiteReader(
                    self.path,
                    ident
                ).package()
            )
        log.info("Segment packaged")
        return self.struct


class FileSystemMaterialSuiteReader(MaterialSuitePackager):
    """
    The packager for pairtree based MaterialSuite serializations

    Given the path where the MaterialSuite is stored, the identifier, and the
    pairtree encapsulation string, packages a MaterialSuite
    """
    @log_aware(log)
    def __init__(self, seg_path, identifier, encapsulation='srf'):
        """
        Create a new FileSystemMaterialSuiteReader

        __Args__

        1. seg_path (str): The path to the location where the MaterialSuite
            is stored
        2. identifier (str): The identifier of the MaterialSuite

        __KWArgs__

        * encapsulation (str): The pairtree encapsulation utilized by the
            serializer. Defaults to "srf" for "Stage Resource Folder"
        """
        super().__init__()
        self.seg_path = seg_path
        self.identifier = identifier
        self.encapsulation = encapsulation
        self.path = Path(self.seg_path, identifier_to_path(identifier),
                         self.encapsulation)

    # Clobber the ABC function here, this is faster and doesn't instantiate
    # a new file for no reason
    @log_aware(log)
    def get_identifier(self, _):
        return self.identifier

    @log_aware(log)
    def get_content(self):
        log.debug('Searching for content')
        p = Path(self.path, 'content.file')
        if p.is_file():
            log.debug("content located")
            return LDRPath(str(p))
        log.debug("Content not found")

    @log_aware(log)
    def get_premis(self):
        log.debug("Searching for PREMIS")
        p = Path(self.path, 'premis.xml')
        if p.is_file():
            log.debug("PREMIS located")
            return LDRPath(str(p))
        log.warn(
            "Premis not found for materialsuite @ {}".format(self.identifier)
        )

    @log_aware(log)
    def get_techmd_list(self):
        log.debug("searching for technical metadata")
        techmds = [LDRPath(x.path) for x in
                   scandir(str(Path(self.path, 'TECHMD')))]
        if not techmds:
            log.debug(
                "No techmd found for materialsuite @ {}".format(self.identifier)
            )
        else:
            log.debug("Techmd located")
            return techmds
