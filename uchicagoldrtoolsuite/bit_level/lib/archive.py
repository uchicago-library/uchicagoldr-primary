from .abc.structure import Structure
from .abc.ldritem import LDRItem
from .ldritemoperations import get_archivable_identifier
from .materialsuite import MaterialSuite

__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Archive(Structure):
    """
    The structure which holds archival contents in the archive environment.
    """
    def __init__(self):
        self.requird_parts = ['identifier', 'segment', 'accessionrecord',
                              'admninnote', 'legalnote']
        self.identifier = get_archivable_identifier(noid=False)
        self.segments_list = []
        self.accession_record_list = []
        self.legalnote_list = []
        self.adminnote_list = []

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

    def iterate_through_a_list(self, a_list):
        for n_item in a_list:
            yield n_item

    def validate_input(self, input):
        for n_input in input:
            if isinstance(n_input, LDRItem):
                pass
            else:
                raise ValueError("must pass an ldritem; you passed " +
                                 " something of type {}".
                                 format(type(n_input).__name__))

    def get_segments_list(self):
        return self.iterate_through_a_list(self.segments_list)

    def set_segments_list(self, value):
        if not isinstance(value, list):
            raise ValueError("Must pass only a Segment Structure to" +
                             " segments_list")

    def get_premis_list(self):
        return self.iterate_through_a_list(self.premis_list)

    def set_premis_list(self, value):
        if not self.validate_input(value):
            raise ValueError("premis_list can only contain LDRItem " +
                             "sub-class instances")
        else:
            self._premis_list = value

    def get_accession_record(self):
        return self.iterate_through_a_list(self.accession_record)

    def set_accession_record(self, value):
        self.validate_input(value)
        self._data_object = value

    accession_record = property(get_accession_record, set_accession_record)
    segment_list = property(get_segments_list, set_segments_list)
    premis_list = property(get_premis_list, set_premis_list)
