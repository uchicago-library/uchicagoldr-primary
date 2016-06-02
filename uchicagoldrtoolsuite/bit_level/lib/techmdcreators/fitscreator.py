from os import makedirs
from os.path import join, dirname, isfile
from uuid import uuid1

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from ..ldritems.ldrpath import LDRPath
from ..ldritems.abc.ldritem import LDRItem
from .abc.technicalmetadatacreator import TechnicalMetadataCreator
from ..ldritems.ldritemoperations import copy
from ....core.lib.bash_cmd import BashCommand


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FITsCreator(TechnicalMetadataCreator):
    def __init__(self, materialsuite, working_dir, timeout=None):
        super().__init__(materialsuite, working_dir, timeout)

    def process(self):
        if not isinstance(self.get_source_materialsuite().get_premis(),
                          LDRItem):
            raise ValueError("All material suites must have a PREMIS record " +
                             "in order to generate technical metadata.")
        premis_file_path = join(self.working_dir, str(uuid1()))
        copy(
            self.get_source_materialsuite().get_premis(),
            LDRPath(premis_file_path)
        )
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
        copy(
            self.get_source_materialsuite().get_content(),
            LDRPath(content_file_path)
        )

        fits_file_path = join(self.working_dir, str(uuid1()))
        cmd = BashCommand(['fits', '-i', content_file_path,
                           '-o', fits_file_path])

        if self.get_timeout() is not None:
            cmd.set_timeout(self.get_timeout())

        cmd.run_command()

        cmd_data = cmd.get_data()

        if isfile(fits_file_path):
            self.get_source_materialsuite().add_technicalmetadata(
                LDRPath(fits_file_path)
            )
            self.handle_premis(cmd_data, self.get_source_materialsuite(),
                               "FITs", True)
        else:
            self.handle_premis(cmd_data, self.get_source_materialsuite(),
                               "FITs", False)
