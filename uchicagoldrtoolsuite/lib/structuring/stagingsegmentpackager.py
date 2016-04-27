
from .segmentpackager import SegmentPackager

class StagingSegmentPackager(SegmentPackager):
    def __init__(self, label_text, label_number):
        self.struct_type = "staging"
            
    def set_type(self, value):
        self._struct_type = value

    def get_type(self):
        return self._struct_type
    
    struct_type = property(get_type, set_type)
