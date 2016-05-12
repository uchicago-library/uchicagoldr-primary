from .abc.structure import Structure
from .abc.ldritem import LDRItem
from .ldritemoperations import get_archivable_identifier
from .materialsuite import MaterialSuite
from .segment import Segment

__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ArchiveStructure(Structure):
    """
    The structure which holds archival contents in the archive environment.
    """
    def __init__(self):
        self.requird_parts = ['identifier', 'segment', 'accessionrecord',
                              'admninnote', 'legalnote']
        self.identifier = get_archivable_identifier(noid=False)
        self.premis_list = []
        self.segments_list = []
        self.accession_record_list = []
        self.technicalmetadata_list = []

    def validate(self):
        super(ArchiveStructure, self)._validate()
        big_list = self.accessionrecord + self.adminnote + self.legalnote
        for n_thing in big_list:
            if getattr(n_thing, LDRItem):
                return False
        for n_thing in self.segment:
            if not getattr(n_thing, MaterialSuite):
                return False
        return True

    def validate_input(self, input):
        for n_input in input:
            if isinstance(n_input, LDRItem):
                pass
            else:
                raise ValueError("must pass an ldritem; you passed " +
                                 " something of type {}".
                                 format(type(n_input).__name__))

    def get_segments_list(self):
        return self._segment_list

    def set_segments_list(self, value):
        if not isinstance(value, Segment):
            raise ValueError("Must pass only a Segment Structure to" +
                             " segments_list")
        sel._segments_list = value

    def get_premis_object(self):
        return self._data_object

    def set_premis_object(self, value):
        self.validate_input(value)
        self._data_object = value

    def get_accession_record(self):
        return self._data_object

    def set_accession_record(self, value):
        self.validate_input(value)
        self._data_object = value

    def get_techmd_object(self):
        return self._data_object

    def set_techmd_object(self, value):
        self.validate_input(value)
        self._technicalmetadata_object = value

    data_object = property(get_data_object, set_data_object)
    preims_object = property(get_premis_object, set_premis_object)
    accession_record = property(get_accession_record, set_accession_record)
    techmd_object = property(get_techmd_object, set_techmd_object)
