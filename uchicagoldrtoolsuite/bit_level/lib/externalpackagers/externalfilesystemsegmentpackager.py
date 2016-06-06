from os.path import isfile
from os.path import join

from ..structures.segment import Segment
from ..readers.abc.segmentpackager import SegmentPackager
from .externalfilesystemmaterialsuitepackager import\
    ExternalFileSystemMaterialSuitePackager
from ..fstools.rootedpath import RootedPath
from ..fstools.filepathtree import FilePathTree


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ExternalFileSystemSegmentPackager(SegmentPackager):
    """
    Reads a segment structure that has been serialized to disk and understands
    how to package it back up as a segment for inclusion in a Staging
    Structure
    """
    def __init__(self, path, label_text, label_number, root=None,
                 filter_pattern=None):
        """
        instantiate a new ExternalFileSystemSegmentPackager with all the
        information that it will need to package the contents of an external
        directory as a segment to be inserted into an existing Stage.

        __Args__

        1. path (str): The path to the external directory whose contents
            are going to be packaged in the segment
        2. label_text (str): The label for the first part of the segments id
        3. label_number (int): The number for the second part of the segments
            id

        __KWArgs__

        * root (str): A path root to remove from the item information, by
            default this will be the containing directory of the specified
            directory
        * filter_pattern (str): A regex to use to specify files not to include
        """
        super().__init__()
        self.filter_pattern = filter_pattern
        self.set_implementation("file system")
        self.set_msuite_packager(ExternalFileSystemMaterialSuitePackager)
        self.set_id_prefix(label_text)
        self.set_id_num(label_number)
        self.set_struct(Segment(self.get_id_prefix(), int(self.get_id_num())))
        self.root = root
        if root:
            self.path = RootedPath(path, root=root)
        else:
            self.path = path

    def package(self):
        """
        read the file system and package things up into a Segment

        __Returns__

        * self.get_struct(): The packaged Segment
        """
        tree = FilePathTree(self.path, filter_pattern=self.filter_pattern)
        if self.root:
            for x in tree.get_paths():
                if not isfile(join(self.root, x)):
                    continue
                ms = self.get_msuite_packager()(join(self.root, x),
                                                root=self.root).package()
                self.get_struct().add_materialsuite(ms)
        else:
            for x in tree.get_paths():
                if not isfile(x):
                    continue
                ms = self.get_msuite_packager()(x).package()
                self.get_struct().add_materialsuite(ms)
        return self.get_struct()
