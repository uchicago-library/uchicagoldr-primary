from json import dumps
from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from .abc.structure import Structure
from .segment import Segment
from ..ldritems.abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class Stage(Structure):
    """
    A Stage is a structure which holds an aggregates contents
    as they are being processed for ingestion into long term storage
    """

    required_parts = ['identifier', 'segment_list', 'accessionrecord_list',
                      'adminnote_list', 'legalnote_list']

    def __init__(self, param1):
        self._identifier = None
        self._segment = []
        self._accessionrecord = []
        self._adminnote = []
        self._legalnote = []
        self.set_identifier(param1)
        log.debug("Stage spawned: {}".format(str(self)))

    def __repr__(self):
        attr_dict = {
            'identifier': self.identifier,
            'segment_list': [str(x) for x in self.segment_list],
            'accessionrecord_list': [str(x) for x in self.accessionrecord_list],
            'adminnote_list': [str(x) for x in self.adminnote_list],
            'legalnote_list': [str(x) for x in self.legalnote_list]
        }
        return "<Stage {}>".format(dumps(attr_dict, sort_keys=True))

    def get_identifier(self):
        return self._identifier

    def set_identifier(self, identifier):
        self._identifier = identifier
        log.debug(
            "Stage ({}) identifier set to {}".format(str(self), identifier)
        )

    def get_segment_list(self):
        return self._segment

    def set_segment_list(self, seg_list):
        self.del_segment_list()
        for x in seg_list:
            self.add_segment(x)

    def del_segment_list(self):
        while self.get_segment_list():
            self.pop_segment()

    def add_segment(self, segment):
        if not isinstance(segment, Segment):
            raise ValueError('only Segments can be added to the segments_list')
        self._segment.append(segment)
        log.debug("Added Segment to Stage: {}".format(str(segment)))

    def get_segment(self, index):
        return self.get_segment_list()[index]

    def pop_segment(self, index=None):
        if index is None:
            return self.get_segment_list().pop()
        else:
            return self.get_segment_list().pop(index)

    def get_accessionrecord_list(self):
        return self._accessionrecord

    def set_accessionrecord_list(self, acc_rec_list):
        self.del_accessionrecord_list()
        for x in acc_rec_list:
            self.add_accessionrecord(x)

    def del_accessionrecord_list(self):
        while self.get_accessionrecord_list():
            self.pop_accessionrecord()

    def add_accessionrecord(self, accrec):
        self._accessionrecord.append(accrec)
        log.debug("Added accession record to Stage: {}".format(str(accrec)))

    def get_accessionrecord(self, index):
        return self.get_accessionrecord_list()[index]

    def pop_accessionrecord(self, index=None):
        if index is None:
            return self.get_accessionrecord_list.pop()
        else:
            return self.get_accessionrecord_list.pop(index)

    def get_adminnote_list(self):
        return self._adminnote

    def set_adminnote_list(self, adminnotelist):
        self.del_adminnote_list()
        for x in adminnotelist:
            self.add_adminnote(x)

    def del_adminnote_list(self):
        while self.get_adminnote_list():
            self.pop_adminnote()

    def add_adminnote(self, adminnote):
        self.get_adminnote_list().append(adminnote)
        log.debug("Added adminnote to Stage: {}".format(str(adminnote)))

    def get_adminnote(self, index):
        return self.get_adminnote_list()[index]

    def pop_adminnote(self, index=None):
        if index is None:
            return self.get_adminnote_list().pop()
        else:
            return self.get_adminnote_list().pop(index)

    def get_legalnote_list(self):
        return self._legalnote

    def set_legalnote_list(self, legalnote_list):
        self.del_legalnote_list()
        for x in legalnote_list:
            self.add_legalnote(x)

    def del_legalnote_list(self):
        while self.get_legalnote_list():
            self.pop_legalnote()

    def add_legalnote(self, legalnote):
        self.get_legalnote_list().append(legalnote)
        log.debug("Added legalnote to Stage: {}".format(str(legalnote)))

    def get_legalnote(self, index):
        return self.get_legalnote_list()[index]

    def pop_legalnote(self, index=None):
        if index is None:
            return self.get_legalnote_list().pop()
        else:
            return self.get_legalnote_list().pop(index)

    def validate(self):
        for n_thing in self.segment_list:
            if isinstance(n_thing, Segment):
                pass
            else:
                return False
        big_list = self.accessionrecord_list + \
            self.adminnote_list + \
            self.legalnote_list
        for n_thing in big_list:
            if isinstance(n_thing, LDRItem):
                pass
            else:
                return False
        return super().validate()

    identifier = property(get_identifier,
                          set_identifier)
    segment_list = property(get_segment_list,
                            set_segment_list,
                            del_segment_list)
    accessionrecord_list = property(get_accessionrecord_list,
                                    set_accessionrecord_list,
                                    del_accessionrecord_list)
    adminnote_list = property(get_adminnote_list,
                              set_adminnote_list,
                              del_adminnote_list)
    legalnote_list = property(get_legalnote_list,
                              set_legalnote_list,
                              del_legalnote_list)
