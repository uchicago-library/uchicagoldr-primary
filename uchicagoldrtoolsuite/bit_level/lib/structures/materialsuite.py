from json import dumps
from logging import getLogger

from .abc.structure import Structure
from ..ldritems.abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class MaterialSuite(Structure):
    """
    A structure which holds all LDR Items pertaining to an "original" and that
    original itself
    """

    required_parts = ['identifier', 'content', 'original', 'premis',
                      'technicalmetadata_list']

    def __init__(self):
        self._content = None
        self._premis = None
        self._technicalmetadata = []
        self._identifier = None

        log.debug("MaterialSuite spawned: {}".format(str(self)))

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

    def get_identifier(self):
        return self._identifier

    def set_identifier(self, x):
        if not isinstance(x, str):
            raise ValueError("Bad materialsuite identifier!")
        self._identifier = x

    def del_identifier(self):
        self.identifier = None

    def set_content(self, content):
        log.debug("Setting content in {} to {}".format(str(self), str(content)))
        self._content = content

    def get_content(self):
        return self._content

    def del_content(self):
        log.debug("Deleting content from MaterialSuite: {}".format(str(self)))
        self._content = None

    def set_premis(self, premis):
        log.debug("Setting PREMIS in {} to {}".format(str(self), str(premis)))
        self._premis = premis

    def get_premis(self):
        return self._premis

    def del_premis(self):
        log.debug("Deleting PREMIS from MaterialSuite: {}".format(str(self)))
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
        if self.get_technicalmetadata_list() is None:
            self._technicalmetadata = []
        if index is None:
            index = len(self.get_technicalmetadata_list())
        self.get_technicalmetadata_list().insert(index, technicalmetadata)
        log.debug("Added technicalmetadata({}) to {}".format(str(technicalmetadata), str(self)))

    def get_technicalmetadata(self, index):
        return self.get_technicalmetadata_list()[index]

    def pop_technicalmetadata(self, index=None):
        if index is None:
            x = self.get_technicalmetadata_list().pop()
        else:
            x = self.get_technicalmetadata_list.pop(index)
        log.debug("Popped technicalmetadata({}) from {}".format(str(x), str(self)))

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
