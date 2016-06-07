from .abc.structure import Structure
from ..ldritems.abc.ldritem import LDRItem
from .segment import Segment

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

    def __init__(self, defined_id=None, make_noid=False):
        self.required_parts = ['identifier', 'segment_list',
                               'accessionrecord_list', 'admninnote_list',
                               'legalnote_list']
        if defined_id:
            self.identifier = defined_id
        else:
            self.identifier = get_archivable_identifier(noid=make_noid)
        self.segment_list = []
        self.accessionrecord_list = []
        self.legalnote_list = []
        self.adminnote_list = []

    def validate(self):
        super().validate()
        big_list = self.accessionrecord_list + self.adminnote_list +\
            self.legalnote_list

        for n_thing in self.segment_list:
            if not isinstance(n_thing, Segment):
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
        return self._segment_list

    def set_segments_list(self, value):
        if not isinstance(value, list):
            raise ValueError("Must pass only a Segment Structure to" +
                             " segments_list")
        else:
            self._segment_list = value

    def get_premis_list(self):
        return self._premis_list

    def set_premis_list(self, value):
        if not self.validate_input(value):
            raise ValueError("premis_list can only contain LDRItem " +
                             "sub-class instances")
        else:
            self._premis_list = value

    def get_accession_record(self):
        return self._Accession_record_list

    def set_accession_record(self, value):
        self.validate_input(value)
        self._data_object = value

    def get_required_parts(self):
        return self._required_parts

    def set_required_parts(self, value):
        self._required_parts = value

    required_parts = property(get_required_parts, set_required_parts)
    accession_record = property(get_accession_record, set_accession_record)
    segment_list = property(get_segments_list, set_segments_list)
    premis_list = property(get_premis_list, set_premis_list)
