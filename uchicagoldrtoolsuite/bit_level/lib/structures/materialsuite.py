from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from .abc.structure import Structure
from ..ldritems.abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class MaterialSuite(Structure):
    """
    A structure which holds all LDR Items pertaining to an "original" and that
    original itself
    """

    required_parts = ['content', 'original', 'premis',
                      'technicalmetadata_list', 'presform_list']

    def __init__(self):
        log.debug("New MaterialSuite created")
        self._content = None
        self._premis = None
        self._technicalmetadata = []
        self._presform = None

    def __repr__(self):
        repr_dict = {}
        repr_dict['content'] = self.get_content()
        repr_dict['premis'] = self.get_premis()
        repr_dict['technicalmetadata'] = self.get_technicalmetadata_list()
        repr_dict['presform'] = self.get_presform_list()
        return str(repr_dict)

    def set_content(self, content):
        log.debug("Setting content to {}".format(str(content)))
        self._content = content

    def get_content(self):
        return self._content

    def del_content(self):
        log.debug("Deleting content from MaterialSuite")
        self._content = None

    def set_premis(self, premis):
        log.debug("Setting PREMIS to {}".format(str(premis)))
        self._premis = premis

    def get_premis(self):
        return self._premis

    def del_premis(self):
        log.debug("Deleting PREMIS from MaterialSuite")
        self._premis = None

    def get_technicalmetadata_list(self):
        return self._technicalmetadata

    def set_technicalmetadata_list(self, technicalmetadata_list):
        self.del_technicalmetadata_list()
        self._technicalmetadata = []
        for x in technicalmetadata_list:
            self.add_technicalmetadata(x)

    def del_technicalmetadata_list(self):
        while self.get_technicalmetadata_list():
            self.pop_technicalmetadata()

    def add_technicalmetadata(self, technicalmetadata, index=None):
        log.debug("Adding {} as technicalmetadata".format(
            str(technicalmetadata)))
        if self.get_technicalmetadata_list() is None:
            self._technicalmetadata = []
        if index is None:
            index = len(self.get_technicalmetadata_list())
        self.get_technicalmetadata_list().insert(index, technicalmetadata)

    def get_technicalmetadata(self, index):
        return self.get_technicalmetadata_list()[index]

    def pop_technicalmetadata(self, index=None):
        log.debug("Popping from technicalmetadata list")
        if index is None:
            return self.get_technicalmetadata_list().pop()
        else:
            return self.get_technicalmetadata_list.pop(index)

    def get_presform_list(self):
        return self._presform

    def set_presform_list(self, presform_list):
        self.del_presform_list()
        self._presform = []
        for x in presform_list:
            self.add_presform(x)

    def del_presform_list(self):
        log.debug("Deleting presform list from MaterialSuite")
        self._presform = None

    def add_presform(self, presform, index=None):
        log.debug("Adding {} to MaterialSuite as presform".format(
            str(presform)))
        if self.get_presform_list() is None:
            self._presform = []
        if index is None:
            index = len(self.get_technicalmetadata_list())
        self.get_presform_list().insert(index, presform)

    def get_presform(self, index):
        return self.get_presform_list()[index]

    def pop_presform(self, index=None):
        log.debug("Popping from presform list")
        if index is None:
            return self.get_presform_list().pop()
        else:
            return self.get_presform_list().pop(index)

    def validate(self):
        if not isinstance(self.get_content(), LDRItem):
            return False
        if self.get_original() is not None:
            if not isinstance(self.get_original(), LDRItem):
                return False
        if self.get_premis() is not None:
            if not isinstance(self.get_premis(), LDRItem):
                return False
        if len(self.get_technicalmetadata_list()) > 0:
            for x in self.get_technicalmetadata_list():
                if not isinstance(x, LDRItem):
                    return False
        if len(self.get_presform_list()) > 0:
            for x in self.get_presform_list():
                if not isinstance(x, MaterialSuite):
                    return False
                if not x.validate():
                    return False
        return super().validate()

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

    presform_list = property(
        get_presform_list,
        set_presform_list,
        del_presform_list
    )
