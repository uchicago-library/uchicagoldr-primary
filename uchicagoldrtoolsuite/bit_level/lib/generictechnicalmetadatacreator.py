from tempfile import TemporaryDirectory
from uuid import uuid1
from os.path import join

from .ldrpath import LDRPath
from ...core.lib.bash_cmd import BashCommand


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class GenericTechnicalMetadataCreator(object):
    """
    Ingests a stage structure and produces a FITS xml record for every
    file in it.
    """
    def __init__(self, stage):
        self.stage = stage
        # This instance var should hold the dir open until the instance is
        # deleted from whatever script spawned it. Aka move this stuff
        # somewhere before your instance gets garbage collected.
        self.working_dir = TemporaryDirectory()
        self.working_dir_path = self.working_dir.name

    def process(self):
        for segment in self.stage.segment_list:
            for materialsuite in segment.materialsuite_list:
                materialsuite.set_technicalmetadata_list(
                    self.instantiate_and_make_techmd(materialsuite.content)
                )

    def instantiate_and_make_techmd(self, item):
        recv_file = join(self.working_dir_path, str(uuid1()))
        fits_file = join(self.working_dir_path, str(uuid1()))
        with item.open('rb') as src:
            with open(recv_file, 'wb') as dst:
                dst.write(src.read(1024))

        com = BashCommand(['fits', '-i', recv_file, '-o', fits_file])
        com.set_timeout(43200)
        com.run_command()

        return [LDRPath(fits_file)]
