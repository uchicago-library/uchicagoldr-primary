from abc import ABCMeta
from json import dumps
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from ..materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class AccessionContainer(metaclass=ABCMeta):
    """
    A Stage is a structure which holds an aggregates contents
    as they are being processed for ingestion into long term storage
    """
    @log_aware(log)
    def __init__(self, identifier):
        """
        Creates a new Stage

        __Args__

        param1 (str): The identifier that will be assigned to the Stage
        """
        log.debug("Entering ABC init")
        self._identifier = None
        self._materialsuite_list = []
        self._accessionrecord = []
        self._adminnote = []
        self._legalnote = []
        self.set_identifier(identifier)
        log.debug("Exiting ABC init")

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'identifier': self.identifier,
            'materialsuite_list': [str(x) for x in self.materialsuite_list],
            'accessionrecord_list': [str(x) for x in self.accessionrecord_list],
            'adminnote_list': [str(x) for x in self.adminnote_list],
            'legalnote_list': [str(x) for x in self.legalnote_list]
        }
        return "<{} {}>".format(str(type(self)),
                                dumps(attr_dict, sort_keys=True))

    @log_aware(log)
    def get_identifier(self):
        return self._identifier

    @log_aware(log)
    def set_identifier(self, identifier):
        log.debug("{}({}) identifier being set to {}".format(
            str(type(self)),
            str(self.identifier), identifier)
        )
        self._identifier = identifier
        log.debug(
            "{} identifier set to {}".format(str(type(self)), identifier)
        )

    @log_aware(log)
    def get_materialsuite_list(self):
        return self._materialsuite_list

    @log_aware(log)
    def set_materialsuite_list(self, x):
        self.del_materialsuite_list()
        for y in x:
            self.add_materialsuite(y)

    @log_aware(log)
    def del_materialsuite_list(self):
        while self.materialsuite_list:
            self.pop_materialsuite()

    @log_aware(log)
    def add_materialsuite(self, x):
        if not isinstance(x, MaterialSuite):
            raise ValueError()
        self._materialsuite_list.append(x)

    @log_aware(log)
    def get_materialsuite(self, index):
        return self.materialsuite_list[index]

    @log_aware(log)
    def pop_materialsuite(self, index=None):
        if index is None:
            self.materialsuite_list.pop()
        else:
            self.materialsuite_list.pop(index)

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
        log.debug("Added accession record to {}({}): ({})".format(
            str(type(self)),
            self.identifier,
            str(accrec))
        )

    @log_aware(log)
    def get_accessionrecord(self, index):
        return self.get_accessionrecord_list()[index]

    @log_aware(log)
    def pop_accessionrecord(self, index=None):
        if index is None:
            x = self.get_accessionrecord_list.pop()
        else:
            x = self.get_accessionrecord_list.pop(index)
        log.debug("Popped accession record from {}({}): {}".format(
            str(type(self)),
            self.identifier,
            str(x))
        )
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
        log.debug("Added adminnote to {}({}): {}".format(
            str(type(self)),
            self.identifier,
            str(adminnote))
        )

    @log_aware(log)
    def get_adminnote(self, index):
        return self.get_adminnote_list()[index]

    @log_aware(log)
    def pop_adminnote(self, index=None):
        if index is None:
            x = self.get_adminnote_list().pop()
        else:
            x = self.get_adminnote_list().pop(index)
        log.debug("Popped adminnote from {}({}): {}".format(
            str(type(self)),
            self.identifier,
            str(x))
        )
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
        log.debug("Added legalnote to {}: {}".format(
            str(type(self)),
            str(legalnote))
        )

    @log_aware(log)
    def get_legalnote(self, index):
        return self.get_legalnote_list()[index]

    @log_aware(log)
    def pop_legalnote(self, index=None):
        if index is None:
            return self.get_legalnote_list().pop()
        else:
            return self.get_legalnote_list().pop(index)

    identifier = property(get_identifier,
                          set_identifier)
    materialsuite_list = property(get_materialsuite_list,
                                  set_materialsuite_list,
                                  del_materialsuite_list)
    accessionrecord_list = property(get_accessionrecord_list,
                                    set_accessionrecord_list,
                                    del_accessionrecord_list)
    adminnote_list = property(get_adminnote_list,
                              set_adminnote_list,
                              del_adminnote_list)
    legalnote_list = property(get_legalnote_list,
                              set_legalnote_list,
                              del_legalnote_list)
