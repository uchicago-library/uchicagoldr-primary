from abc import abstractproperty

from .packager import Packager


class SegmentPackager(Packager):

    def set_msuite_packager(self, value):
        self.msuite_packager = value

    def get_msuite_packager(self):
        return self.msuite_packager

    def set_id_prefix(self, value):
        self._id_prefix = value

    def get_id_prefix(self):
        return self._id_prefix

    def set_id_num(self, value):
        self._id_num = value

    def get_id_num(self):
        return self._id_num

    msuite_packager = abstractproperty(get_msuite_packager, set_msuite_packager)
    id_prefix = abstractproperty(get_id_prefix, set_id_prefix)
    id_num = abstractproperty(get_id_num, set_id_num)
