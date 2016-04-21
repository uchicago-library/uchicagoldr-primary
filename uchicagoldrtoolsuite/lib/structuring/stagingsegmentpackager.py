
from .segmentpackager import SegmentPackager

class StagingSegmentPackager(SegmentPackager):
    def __init__(self, struct_type):
        self.struct_type = "staging"
        
    def set_struct(self, value):
        self._struct

    def get_struct(self):
        return self._struct

    def set_type(self, value):
        self._struct_type = value

    def get_type(self):
        return self._struct_type

    def get_implementation(self):
        return self._implementation

    def set_implementation(self, value):
        self._implementation = value

    def get_msuite_packager(self):
        return self._msuite_packager

    def set_msuite_packager(self, value):
        self._msuite_packager = value

    def get_id_prefix(self):
        return self._id_prefix

    def set_id_prefix(self, value):
        self._id_prefix = value

    def set_id_num(self, value):
        self._id_num = value

    def get_id_num(self):
        return self._id_num
        
    struct = property(get_struct, set_struct)
    struct_type = property(get_type, set_type)
    implementation = property(get_implementation, set_implementation)
    msuite_packager = property(get_msuite_packager, set_msuite_packager)
    id_prefix = property(get_id_prefix, set_id_prefix)
    id_num = property(get_id_num, set_id_num)
