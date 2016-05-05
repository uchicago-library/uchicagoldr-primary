from os.path import isfile

from .absolutefilepathtree import AbsoluteFilePathTree
from .segment import Segment
from .abc.segmentpackager import SegmentPackager
from .externalfilesystemmaterialsuitepackager import\
    ExternalFileSystemMaterialSuitePackager
from .ldrpath import LDRPath


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
    def __init__(self, label_text, label_number):
        super().__init__()
        self.set_implementation("file system")
        self.set_msuite_packager(ExternalFileSystemMaterialSuitePackager)
        self.set_id_prefix(label_text)
        self.set_id_num(label_number)
        self.set_struct(Segment(self.get_id_prefix(), int(self.get_id_num())))

    def package(self, a_directory, remainder_files=[]):
        if len(remainder_files) <= 0:
            tree = AbsoluteFilePathTree(a_directory)
            just_files = tree.get_files()
            for n_thing in just_files:
                a_file = LDRPath(n_thing)
                packager = self.msuite_packager(a_file)
                msuite = packager.package()
                self.get_struct().add_material_suite(msuite)
        else:
            for n_item in remainder_files:
                if isfile(n_item):
                    a_thing = LDRPath(n_item)
                msuite = packager.package(a_thing)
                self.get_struct().add_material_suite(msuite)
        return self.get_struct()
