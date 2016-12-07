from pathlib import Path
from logging import getLogger
from os import scandir

from pypairtree.utils import path_to_identifier

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success, recursive_scandir
from .filesystemmaterialsuitereader import FileSystemMaterialSuiteReader
from .abc.stageserializationreader import StageSerializationReader
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
    def __init__(
        self, root, target_identifier, encapsulation='srf',
        materialsuite_deserializer=FileSystemMaterialSuiteReader,
        materialsuite_deserializer_kwargs={}
    ):
        """
        Create a new FileSystemStageReader

        __Args__

        1. root (str): The path to the staging environment
        2. target_identifier (str): An identifier for a stage in the staging
            environment

        __KWArgs__

        * encapsulation (str): The encapsulation to use in this serialization,
            if none is provided explicitly in the materialsuite deserializer
            kwargs this value will be inherited by the materialsuite
            deserializer
        * materialsuite_deserializer (.abc.MaterialsuiteSerializationReader):
            A class to delegate reading the MaterialSuites to
        * materialsuite_deserializer_kwargs (dict): kwargs to pass to the class
            that is delegated to.
        """
        log_init_attempt(self, log, locals())
        super().__init__(root, target_identifier, materialsuite_deserializer,
                         materialsuite_deserializer_kwargs)
        self.path = str(Path(self.root, self.target_identifier))
        self.encapsulation = encapsulation
        # If the ms deserializer needs encapsulation inherit it if none is
        # provided
        if not 'encapsulation' in self.materialsuite_deserializer_kwargs.keys():
            self.materialsuite_deserializer_kwargs['encapsulation'] = \
                self.encapsulation
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
                self.materialsuite_deserializer(
                    materialsuites_dir,
                    path_to_identifier(Path(x).parent, root=materialsuites_dir),
                    **self.materialsuite_deserializer_kwargs
                ).read()
            )
        log.info("Stage read")
        return self.struct
