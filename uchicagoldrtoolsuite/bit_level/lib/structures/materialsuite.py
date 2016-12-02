from json import dumps
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from ..ldritems.abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class MaterialSuite(object):
    """
    A structure which holds all LDR Items pertaining to a piece of content
    and the content itself
    """
    @log_aware(log)
    def __init__(self):
        """
        Creates a new MaterialSuite
        """
        log_init_attempt(self, log, locals())
        self._content = None
        self._premis = None
        self._technicalmetadata = []
        self._identifier = None
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'identifier': self.identifier,
            'content': str(self.get_content()),
            'premis': str(self.get_premis())
        }
        if self.technicalmetadata_list:
            attr_dict['technicalmetadata_list'] = [str(x) for x in self.technicalmetadata_list]
        else:
            attr_dict['technicalmetadata_list'] = None
        return "<MaterialSuite {}>".format(dumps(attr_dict, sort_keys=True))

    @log_aware(log)
    def get_identifier(self):
        return self._identifier

    @log_aware(log)
    def set_identifier(self, x):
        if not isinstance(x, str):
            raise ValueError("Bad materialsuite identifier!")
        self._identifier = x

    @log_aware(log)
    def del_identifier(self):
        self.identifier = None

    @log_aware(log)
    def set_content(self, content):
        log.debug("Setting content in {} to {}".format(str(self), str(content)))
        self._content = content

    @log_aware(log)
    def get_content(self):
        return self._content

    @log_aware(log)
    def del_content(self):
        log.debug("Deleting content from MaterialSuite: {}".format(str(self)))
        self._content = None

    @log_aware(log)
    def set_premis(self, premis):
        log.debug("Setting PREMIS in {} to {}".format(str(self), str(premis)))
        self._premis = premis

    @log_aware(log)
    def get_premis(self):
        return self._premis

    @log_aware(log)
    def del_premis(self):
        log.debug("Deleting PREMIS from MaterialSuite: {}".format(str(self)))
        self._premis = None

    @log_aware(log)
    def get_technicalmetadata_list(self):
        return self._technicalmetadata

    @log_aware(log)
    def set_technicalmetadata_list(self, technicalmetadata_list):
        self.del_technicalmetadata_list()
        self._technicalmetadata = []
        for x in technicalmetadata_list:
            self.add_technicalmetadata(x)

    @log_aware(log)
    def del_technicalmetadata_list(self):
        while self.get_technicalmetadata_list():
            self.pop_technicalmetadata()

    @log_aware(log)
    def add_technicalmetadata(self, technicalmetadata, index=None):
        if self.get_technicalmetadata_list() is None:
            self._technicalmetadata = []
        if index is None:
            index = len(self.get_technicalmetadata_list())
        self.get_technicalmetadata_list().insert(index, technicalmetadata)
        log.debug("Added technicalmetadata({}) to {}".format(str(technicalmetadata), str(self)))

    @log_aware(log)
    def get_technicalmetadata(self, index):
        return self.get_technicalmetadata_list()[index]

    @log_aware(log)
    def pop_technicalmetadata(self, index=None):
        if index is None:
            x = self.get_technicalmetadata_list().pop()
        else:
            x = self.get_technicalmetadata_list.pop(index)
        log.debug("Popped technicalmetadata({}) from {}".format(str(x), str(self)))

    @log_aware(log)
    def validate(self):
        """
        Determines if a MaterialSuite is well formed
        """
        if self.get_premis() is not None:
            if not isinstance(self.get_premis(), LDRItem):
                return False
        if self.get_content() is not None and \
                not len(self.get_technicalmetadata_list()) > 0:
            return False
        if len(self.get_technicalmetadata_list()) > 0:
            for x in self.get_technicalmetadata_list():
                if not isinstance(x, LDRItem):
                    return False
        return super().validate()

    identifier = property(
        get_identifier,
        set_identifier,
        del_identifier
    )

    content = property(
        get_content,
        set_content,
        del_content
    )

    premis = property(
        get_premis,
        set_premis,
        del_premis
    )

    technicalmetadata_list = property(
        get_technicalmetadata_list,
        set_technicalmetadata_list,
        del_technicalmetadata_list
    )
