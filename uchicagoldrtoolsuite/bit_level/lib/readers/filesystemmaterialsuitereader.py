from pathlib import Path
from logging import getLogger
from os import scandir

from pypairtree.utils import identifier_to_path

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from .abc.materialsuiteserializationreader import \
    MaterialSuiteSerializationReader
from ..ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class FileSystemMaterialSuiteReader(MaterialSuiteSerializationReader):
    """
    The packager for pairtree based MaterialSuite serializations

    Given the path where the MaterialSuite is stored, the identifier, and the
    pairtree encapsulation string, packages a MaterialSuite
    """
    @log_aware(log)
    def __init__(self, root, target_identifier, encapsulation='srf'):
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
        log_init_attempt(self, log, locals())
        super().__init__(root, target_identifier)
        self.encapsulation = encapsulation
        self.path = Path(self.root, identifier_to_path(self.target_identifier),
                         self.encapsulation)
        log_init_success(self, log)

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
            "Premis not found for materialsuite @ {}".format(self.target_identifier)
        )

    @log_aware(log)
    def get_techmd_list(self):
        log.debug("searching for technical metadata")
        techmds = [LDRPath(x.path) for x in
                   scandir(str(Path(self.path, 'TECHMD')))]
        if not techmds:
            log.debug(
                "No techmd found for materialsuite @ {}".format(self.target_identifier)
            )
        else:
            log.debug("Techmd located")
            return techmds
