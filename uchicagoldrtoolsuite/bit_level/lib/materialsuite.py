from .abc.structure import Structure
from .abc.ldritem import LDRItem


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class MaterialSuite(Structure):
    """
    A structure which holds all LDR Items pertaining to an "original" and that
    original itself
    """

    required_parts = ['original', 'premis',
                      'technicalmetadata_list', 'presform_list']

    def __init__(self):
        self._content = None
        self._original = None
        self._premis = None
        self._technicalmetadata = []
        self._presform = []

    def set_content(self, original):
        self._original = original

    def get_content(self):
        return self._content

    def del_content(self):
        self._content = None

    def set_original(self, original):
        self._original = original

    def get_original(self):
        return self._original

    def del_original(self):
        self._original = None

    def set_premis(self, premis):
        self._premis = premis

    def get_premis(self):
        return self._premis

    def del_premis(self):
        self._premis = None

    def get_technicalmetadata_list(self):
        return self._technicalmetadata

    def set_technicalmetadata_list(self, technicalmetadata_list):
        self.del_technicalmetadata_list()
        for x in technicalmetadata_list:
            self.add_technicalmetadata(x)

    def del_technicalmetadata_list(self):
        while self.get_technicalmetadata_list():
            self.get_technicalmetadata_list().pop()

    def add_technicalmetadata(self, technicalmetadata, index=None):
        if index is None:
            index = len(self.get_technicalmetadata_list())
        self.get_technicalmetadata_list().insert(index, technicalmetadata)

    def get_technicalmetadata(self, index):
        return self.get_technicalmetadata_list[index]

    def pop_technicalmetadata(self, index=None):
        if index is None:
            return self.get_technicalmetadata_list().pop()
        else:
            return self.get_technicalmetadata_list.pop(index)

    def get_presform_list(self):
        return self._presform

    def set_presform_list(self, presform_list):
        self.del_presform_list()
        for x in presform_list:
            self.add_presform(x)

    def del_presform_list(self):
        while self.get_presform_list():
            self.get_presform_list().pop()

    def add_presform(self, presform, index=None):
        if index is None:
            index = len(self.get_technicalmetadata_list())
        self.get_presform_list().insert(index, presform)

    def get_presform(self, index):
        return self.get_presform_list[index]

    def pop_presform(self, index=None):
        if index is None:
            return self.get_presform_list().pop()
        else:
            return self.get_presform_list().pop(index)

    def validate(self):
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

    original = property(
        get_original,
        set_original,
        del_original
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
