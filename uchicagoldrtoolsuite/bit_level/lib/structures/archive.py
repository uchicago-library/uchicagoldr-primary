from json import dumps
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from .abc.structure import Structure
from ..ldritems.abc.ldritem import LDRItem
from .segment import Segment
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, log_init_success

__author__ = "Tyler Danstrom, Brian Balsamo"
__email__ = "tdanstrom@uchicago.edu, balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class Archive(Structure):
    """
    The structure which holds archival contents in the archive environment.
    """
    @log_aware(log)
    def __init__(self, identifier):
        """
        create a new Archive structure

        __Args__

        1. identifier (str): The identifier of the archive structure
        """
        log_init_attempt(self, log, locals())
        self._identifier = None
        self._segment = []
        self._accessionrecord = []
        self._adminnote = []
        self._legalnote = []
        self._required_parts = None

        self.required_parts = ['identifier', 'segment_list',
                               'accessionrecord_list', 'adminnote_list',
                               'legalnote_list']
        self.identifier = identifier
        self.segment_list = []
        self.accessionrecord_list = []
        self.legalnote_list = []
        self.adminnote_list = []
        log_init_success(self, log)

    @log_aware(log)
    def _validate_materialsuite(self, materialsuite):
        """
        Determines a MaterialSuite is valid for inclusion in an Archive struct
        """
        log.debug("Validating MaterialSuite for inclusion in an Archive")
        try:
            if not isinstance(materialsuite.content, LDRItem) and \
                    not isinstance(materialsuite.content, type(None)):
                log.warn("Incorrect object (not LDRItem or None) in a " +
                         "MaterialSuite content slot")
                return False
            if not isinstance(materialsuite.premis, LDRItem):
                log.warn("MaterialSuite missing PREMIS metadata")
                return False
            # TODO: Decide if mandating technical metadata (when there's
            # content) is a solid idea, is this an implementation specific
            # detail?
            if not len(materialsuite.technicalmetadata_list) > 0 and \
                    isinstance(materialsuite.content, LDRItem):
                log.warn("Content exists with no technical metadata")
                return False
        except Exception as e:
            log.critical("Problem in MaterialSuite validation")
            return False
        return True

    @log_aware(log)
    def validate(self):
        """
        Determines if the structure includes all the required components
        and that they are all well formed.
        """
        log.info("Validating included components")
        for segment in self.segment_list:
            for materialsuite in segment.materialsuite_list:
                if self._validate_materialsuite(materialsuite) is False:
                    log.warn("A MaterialSuite is malformed")
                    return False
        if len(self.accessionrecord_list) < 1:
            log.warn("Missing an accession record")
            return False
        return super().validate()

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'identifier': self.identifier,
            'segment_list': [str(x) for x in self.segment_list],
            'accessionrecord_list': [str(x) for x in self.accessionrecord_list],
            'adminnote_list': [str(x) for x in self.adminnote_list],
            'legalnote_list': [str(x) for x in self.legalnote_list]
        }
        return "<Archive {}>".format(dumps(attr_dict, sort_keys=True))

    @log_aware(log)
    def get_identifier(self):
        return self._identifier

    @log_aware(log)
    def set_identifier(self, identifier):
        log.debug("Archive({}) identifier being set to {}".format(str(self.identifier), self.identifier))
        self._identifier = identifier
        log.debug(
            "Archive identifier set to {}".format(identifier)
        )

    @log_aware(log)
    def get_segment_list(self):
        return self._segment

    @log_aware(log)
    def set_segment_list(self, seg_list):
        self.del_segment_list()
        for x in seg_list:
            self.add_segment(x)

    @log_aware(log)
    def del_segment_list(self):
        while self.get_segment_list():
            self.pop_segment()

    @log_aware(log)
    def add_segment(self, segment):
        if not isinstance(segment, Segment):
            raise ValueError('only Segments can be added to the segments_list')
        self._segment.append(segment)
        log.debug("Added Segment({}) to Archive({}): {}".format(segment.identifier, self.identifier, str(segment)))

    @log_aware(log)
    def get_segment(self, index):
        return self.get_segment_list()[index]

    @log_aware(log)
    def pop_segment(self, index=None):
        if index is None:
            x = self.get_segment_list().pop()
        else:
            x = self.get_segment_list().pop(index)
        log.debug("Popped segment({}) from Archive({})".format(x.identifier, self.identifier))
        return x

    @log_aware(log)
    def get_accessionrecord_list(self):
        return self._accessionrecord

    @log_aware(log)
    def set_accessionrecord_list(self, acc_rec_list):
        self.del_accessionrecord_list()
        for x in acc_rec_list:
            self.add_accessionrecord(x)

    @log_aware(log)
    def del_accessionrecord_list(self):
        while self.get_accessionrecord_list():
            self.pop_accessionrecord()

    @log_aware(log)
    def add_accessionrecord(self, accrec):
        self._accessionrecord.append(accrec)
        log.debug("Added accession record to Archive({}): {}".format(self.identifier, str(accrec)))

    @log_aware(log)
    def get_accessionrecord(self, index):
        return self.get_accessionrecord_list()[index]

    @log_aware(log)
    def pop_accessionrecord(self, index=None):
        if index is None:
            x = self.get_accessionrecord_list.pop()
        else:
            x = self.get_accessionrecord_list.pop(index)
        log.debug("Popped accession record from Archive({}): {}".format(self.identifier, str(x)))
        return x

    @log_aware(log)
    def get_adminnote_list(self):
        return self._adminnote

    @log_aware(log)
    def set_adminnote_list(self, adminnotelist):
        self.del_adminnote_list()
        for x in adminnotelist:
            self.add_adminnote(x)

    @log_aware(log)
    def del_adminnote_list(self):
        while self.get_adminnote_list():
            self.pop_adminnote()

    @log_aware(log)
    def add_adminnote(self, adminnote):
        self.get_adminnote_list().append(adminnote)
        log.debug("Added adminnote to Archive({}): {}".format(self.identifier, str(adminnote)))

    @log_aware(log)
    def get_adminnote(self, index):
        return self.get_adminnote_list()[index]

    @log_aware(log)
    def pop_adminnote(self, index=None):
        if index is None:
            x = self.get_adminnote_list().pop()
        else:
            x = self.get_adminnote_list().pop(index)
        log.debug("Popped adminnote from Archive({}): {}".format(self.identifier, str(x)))
        return x

    @log_aware(log)
    def get_legalnote_list(self):
        return self._legalnote

    @log_aware(log)
    def set_legalnote_list(self, legalnote_list):
        self.del_legalnote_list()
        for x in legalnote_list:
            self.add_legalnote(x)

    @log_aware(log)
    def del_legalnote_list(self):
        while self.get_legalnote_list():
            self.pop_legalnote()

    @log_aware(log)
    def add_legalnote(self, legalnote):
        self.get_legalnote_list().append(legalnote)
        log.debug("Added legalnote to Archive: {}".format(str(legalnote)))

    @log_aware(log)
    def get_legalnote(self, index):
        return self.get_legalnote_list()[index]

    @log_aware(log)
    def pop_legalnote(self, index=None):
        if index is None:
            return self.get_legalnote_list().pop()
        else:
            return self.get_legalnote_list().pop(index)

    @log_aware(log)
    def get_required_parts(self):
        return self._required_parts

    @log_aware(log)
    def set_required_parts(self, value):
        self._required_parts = value

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
    required_parts = property(get_required_parts, set_required_parts)
