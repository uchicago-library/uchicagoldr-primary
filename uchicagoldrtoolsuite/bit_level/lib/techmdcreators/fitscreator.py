from os import makedirs, remove
from os.path import join, dirname, isfile
from uuid import uuid1

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from ..ldritems.ldrpath import LDRPath
from ..ldritems.abc.ldritem import LDRItem
from .abc.technicalmetadatacreator import TechnicalMetadataCreator
from ..ldritems.ldritemcopier import LDRItemCopier
from uchicagoldrtoolsuite.core.lib.bash_cmd import BashCommand


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class FITsCreator(TechnicalMetadataCreator):
    def __init__(self, materialsuite, working_dir, timeout=None):
        log.debug("FITsCreator spawned. Processing {}".format(str(materialsuite.content)))
        super().__init__(materialsuite, working_dir, timeout)

    def process(self):
        if not isinstance(self.get_source_materialsuite().get_premis(),
                          LDRItem):
            raise ValueError("All material suites must have a PREMIS record " +
                             "in order to generate technical metadata.")
        log.debug("Building FITS-ing environment")
        premis_file_path = join(self.working_dir, str(uuid1()))
        LDRItemCopier(
            self.get_source_materialsuite().get_premis(),
            LDRPath(premis_file_path)
        ).copy()
        premis_record = PremisRecord(frompath=premis_file_path)
        original_name = premis_record.get_object_list()[0].get_originalName()

        content_file_path = dirname(
            join(
                self.working_dir,
                str(uuid1()),
                original_name
            )
        )
        content_file_containing_dir_path = dirname(content_file_path)
        makedirs(content_file_containing_dir_path, exist_ok=True)
        original_holder = LDRPath(content_file_path)
        LDRItemCopier(
            self.get_source_materialsuite().get_content(),
            original_holder
        ).copy()

        fits_file_path = join(self.working_dir, str(uuid1()))
        cmd = BashCommand(['fits', '-i', content_file_path,
                           '-o', fits_file_path])

        if self.get_timeout() is not None:
            cmd.set_timeout(self.get_timeout())

        log.debug("Running FITS on file. Timeout: {}".format(str(self.get_timeout())))
        cmd.run_command()

        cmd_data = cmd.get_data()

        if isfile(fits_file_path):
            log.debug("FITS successfully created")
            self.get_source_materialsuite().add_technicalmetadata(
                LDRPath(fits_file_path)
            )
            self.handle_premis(cmd_data, self.get_source_materialsuite(),
                               "FITs", True)
        else:
            log.debug("FITS creation failed.")
            self.handle_premis(cmd_data, self.get_source_materialsuite(),
                               "FITs", False)

        log.debug("Cleaning up temporary file instantiation")
        original_holder.delete(final=True)
