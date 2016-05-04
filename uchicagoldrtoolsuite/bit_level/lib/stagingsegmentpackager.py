from .segmentpackager import SegmentPackager


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class StagingSegmentPackager(SegmentPackager):
    def __init__(self, label_text, label_number):
        self.struct_type = "staging"

    def set_type(self, value):
        self._struct_type = value

    def get_type(self):
        return self._struct_type

    struct_type = property(get_type, set_type)
