from .abc.structure import Structure
from .segmentstructure import SegmentStructure
from .abc.ldritem import LDRItem


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class StagingStructure(Structure):
    def __init__(self, param1):
        self.required_parts = ['identifier', 'segment', 'accessionrecord',
                               'adminnote', 'legalnote']
        self.identifier = param1
        self.segment = []
        self.accessionrecord = []
        self.adminnote = []
        self.legalnote = []

    def validate(self):
        for n_thing in self.segment:
            if isinstance(n_thing, SegmentStructure):
                pass
            else:
                return False
        big_list = self.accessionrecord + self.adminnote + self.legalnote
        for n_thing in big_list:
            if isinstance(n_thing, LDRItem):
                pass
            else:
                return False
        return super(StagingStructure, self)._validate()
