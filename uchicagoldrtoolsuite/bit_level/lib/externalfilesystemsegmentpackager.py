from os.path import isfile
from os.path import join

from .segment import Segment
from .abc.segmentpackager import SegmentPackager
from .externalfilesystemmaterialsuitepackager import\
    ExternalFileSystemMaterialSuitePackager
from .rootedpath import RootedPath
from .filepathtree import FilePathTree


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
    def __init__(self, path, label_text, label_number, root=None):
        super().__init__()
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
        tree = FilePathTree(self.path)
        if self.root:
            for x in tree.get_paths():
                if not isfile(join(self.root, x)):
                    continue
                ms = self.get_msuite_packager(join(self.root, x),
                                              root=self.root).package()
                self.get_struct().add_materialsuite(ms)
        else:
            for x in tree.get_paths():
                if not isfile(x):
                    continue
                ms = self.get_msuite_packager()(x).package()
                self.get_struct().add_materialsuite(ms)
        return self.get_struct()
