from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from pathlib import Path
from os.path import join
from uuid import uuid1
from .bash_cmd import BashCommand


class TechnicalMetadataRecordCreator(object):
    def __init__(self, path, timeout=None):
        self.file_path = Path(path)
        if not self.file_path.is_file():
            raise ValueError("The technical metadata creator requires " +
                             "an existing filepath as input.")
        self.record = self.make_record(self.file_path)

    def make_record(self, file_path, timeout=None):
        return make_fits_in_tmp

    def make_fits_in_tmp(self, file_pathi, timeout=None):
        with TemporaryDirectory() as tmpdir:
            outfilename = str(uuid1())
            cmd = BashCommand(['fits', '-i', self.file_path.path, '-o',
                               outfilename])
            if timeout:
                cmd.set_timeout(timeout)
            cmd.run_command()
            if not cmd.get_data()[2]:
                raise OSError("Your fits command did not complete.")
            return self.read_fits(join(tmpdir, outfilename))

    def read_fits(self, fits_path):
        tree = ET.parse(fits_path)
        return tree

    def get_record(self):
        return self.record
