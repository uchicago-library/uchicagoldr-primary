from os.path import join
from os.path import isfile
from re import compile as re_compile

from ..fstools.rootedpath import RootedPath
from ..fstools.filepathtree import FilePathTree
from ..structures.segment import Segment
from .abc.segmentpackager import SegmentPackager
from .filesystemmaterialsuitepackager import\
    FileSystemMaterialSuitePackager


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemSegmentPackager(SegmentPackager):
    """
    Reads a segment structure that has been serialized to disk and understands
    how to package it back up as a segment for inclusion in a Staging
    Structure
    """
    def __init__(self, stage_env_path, stage_id, label_text, label_number):
        """
        spawn a packager

        __Args__

        1. stage_env_path (str): The file system path to the staging environment
        2. stage_id (str): The stage identifier for the stage on disk
        3. label_text (str): The text that makes up the first part of the
            segment identifier
        4. label_number (int): The number that makes up the second part of
            the segment identifier
        """
        super().__init__()
        self.stage_env_path = stage_env_path
        self.stage_id = stage_id
        self.label_text = label_text
        self.label_number = label_number
        self.set_implementation("file system")
        self.set_msuite_packager(FileSystemMaterialSuitePackager)
        self.segment_data_root = join(stage_env_path, stage_id,
                                      'data',
                                      label_text + "-" + str(label_number))
        self.set_struct(Segment(label_text, int(label_number)))

    def package(self):
        presform_filename_pattern = re_compile(
            "^.*\.presform(\.[a-zA-Z0-9]*)?$"
        )
        segment_rooted_path = RootedPath(
            self.segment_data_root+"/",
            root=self.segment_data_root
        )
        tree = FilePathTree(segment_rooted_path)
        for x in tree.get_paths():
            if not isfile(join(self.segment_data_root, x)):
                # Its a directory
                continue
            if presform_filename_pattern.match(x):
                # Its a presform
                continue
            ms = FileSystemMaterialSuitePackager(
                self.stage_env_path,
                self.stage_id,
                self.label_text,
                self.label_number,
                x
            ).package()
            self.get_struct().add_materialsuite(ms)
        return self.get_struct()
