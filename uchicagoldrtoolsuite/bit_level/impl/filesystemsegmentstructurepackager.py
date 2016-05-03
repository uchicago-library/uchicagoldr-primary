from os.path import isfile

from ..lib.absolutefilepathtree import AbsoluteFilePathTree
from ..lib.segmentstructure import SegmentStructure
from ..lib.stagingstructure import StagingStructure
from ..lib.stagingsegmentpackager import StagingSegmentPackager
from .filesystemmaterialsuitestructurepackager import\
    FileSystemMaterialSuiteStructurePackager
from .ldrpath import LDRPath


class FileSystemSegmentStructurePackager(StagingSegmentPackager):
    def __init__(self, label_text, label_number):
        self.struct_type = "staging"
        self.struct = StagingStructure
        self.implementation = "directory"
        self.msuite_packager = FileSystemMaterialSuiteStructurePackager
        self.id_prefix = label_text
        self.id_num = label_number

    def get_material_suites(self):
        return []

    def package(self, a_directory, remainder_files=[]):
        newsegment = SegmentStructure(self.id_prefix, int(self.id_num))
        packager = self.msuite_packager()
        if len(remainder_files) <= 0:
            tree = AbsoluteFilePathTree(a_directory)
            just_files = tree.get_files()
            for n_thing in just_files:
                a_file = LDRPath(n_thing)
                msuite = packager.package(a_file)
                newsegment.materialsuite.append(msuite)
        else:
            for n_item in remainder_files:
                if isfile(n_item):
                    a_thing = LDRPath(n_item)
                msuite = packager.package(a_thing)
                newsegment.materialsuite.append(msuite)
        return newsegment

    def set_struct(self, value):
        self._struct = value

    def get_struct(self):
        return self._struct

    def set_implementation(self, value):
        self._implementation = value

    def get_implementation(self):
        return self._implementation

    def set_msuite_packager(self, value):
        self._msuite_packager = value

    def get_msuite_packager(self):
        return self._msuite_packager

    def set_id_prefix(self, value):
        self._id_prefix = value

    def get_id_prefix(self):
        return self._id_prefix

    def set_id_num(self, value):
        self._id_num = value

    def get_id_num(self):
        return self._id_num

    implementation = property(get_implementation, set_implementation)
    msuite_packager = property(get_msuite_packager, set_msuite_packager)
    id_prefix = property(get_id_prefix, set_id_prefix)
    id_num = property(get_id_num, set_id_num)
    struct = property(get_struct, set_struct)
