from pathlib import Path
from logging import getLogger
from os import scandir

from pypairtree.utils import path_to_identifier, identifier_to_path

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success, recursive_scandir
from .abc.stageserializationreader import StageSerializationReader
from .abc.materialsuitepackager import MaterialSuitePackager
from ..ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


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
    def __init__(self, path, encapsulation='srf'):
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
        self.encapsulation = encapsulation
        log_init_success(self, log)

    @log_aware(log)
    def assert_skeleton(self):
        accessionrecords_dir = Path(self.path, 'admin', 'accessionrecords')
        legalnotes_dir = Path(self.path, 'admin', 'legalnotes')
        adminnotes_dir = Path(self.path, 'admin', 'adminnotes')
        segments_dir = Path(self.path, 'pairtree_root')
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
        materialsuites_dir = Path(self.path, 'pairtree_root')

        log.debug("Adding accession records")
        for x in [x.path for x in scandir(str(accessionrecords_dir))]:
            self.struct.add_accessionrecord(LDRPath(x))
        log.debug("Adding legalnotes")
        for x in [x.path for x in scandir(str(legalnotes_dir))]:
            self.struct.add_legalnote(LDRPath(x))
        log.debug("Adding adminnotes")
        for x in [x.path for x in scandir(str(adminnotes_dir))]:
            self.struct.add_adminnote(LDRPath(x))
        log.debug("Adding MaterialSuites resulting from delegation to the " +
                  "FileSystemMaterialSuite")
        # This isn't particularly pretty, and might be able to be optimized to
        # be more general (and potentially auto-detect the encapsulation) but it
        # works for now.
        for x in (x.path for x in recursive_scandir(str(materialsuites_dir)) if
                  x.name == self.encapsulation):
            self.struct.add_materialsuite(
                FileSystemMaterialSuiteReader(
                    materialsuites_dir,
                    path_to_identifier(Path(x).parent, root=materialsuites_dir),
                    encapsulation=self.encapsulation
                ).package()
            )
        log.info("Stage read")
        return self.struct


class FileSystemMaterialSuiteReader(MaterialSuitePackager):
    """
    The packager for pairtree based MaterialSuite serializations

    Given the path where the MaterialSuite is stored, the identifier, and the
    pairtree encapsulation string, packages a MaterialSuite
    """
    @log_aware(log)
    def __init__(self, root_path, identifier, encapsulation='srf'):
        """
        Create a new FileSystemMaterialSuiteReader

        __Args__

        1. root_path (str): The path to the location where the MaterialSuite
            is stored
        2. identifier (str): The identifier of the MaterialSuite

        __KWArgs__

        * encapsulation (str): The pairtree encapsulation utilized by the
            serializer. Defaults to "srf" for "Stage Resource Folder"
        """
        super().__init__()
        self.root_path = root_path
        self.identifier = identifier
        self.encapsulation = encapsulation
        self.path = Path(self.root_path, identifier_to_path(identifier),
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
        p = Path(self.path, 'premis.xml')
        log.debug("Searching for PREMIS @ {}".format(str(p)))
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
