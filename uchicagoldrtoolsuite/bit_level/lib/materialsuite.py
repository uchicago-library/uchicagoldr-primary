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
    def __init__(self):
        self.required_parts = ['original', 'premis',
                               'technicalmetadata', 'presform']
        self._original = []
        self._premis = []
        self._technicalmetadata = []
        self._presform = []

    def get_original_list(self):
        return self._original

    def set_original_list(self, original_list):
        self.del_original_list()
        for x in original_list:
            self.add_original(x)

    def del_original_list(self):
        while self.get_original_list():
            self.get_original_list().pop()

    def add_original(self, original, index=None):
        if index is None:
            index = len(self.get_original_list())
        self.get_original_list().insert(index, original)

    def get_original(self, index):
        return self.get_original_list()[index]

    def pop_original(self, index=None):
        if index is None:
            return self.get_original_list().pop()
        else:
            return self.get_original_list().pop(index)

    def get_premis_list(self):
        return self._premis

    def set_premis_list(self, premis_list):
        self.del_premis_list()
        for x in premis_list:
            self.add_premis(x)

    def del_premis_list(self):
        while self.get_premis_list():
            self.get_premis_list().pop()

    def add_premis(self, premis, index=None):
        if index is None:
            index = len(self.get_premis_list())
        self.get_premis_list().insert(index, premis)

    def get_premis(self, index):
        return self.get_premis_list()[index]

    def pop_premis(self, index=None):
        if index is None:
            return self.get_premis_list().pop()
        else:
            return self.get_premis_list().pop(index)

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
        pass

    def set_presform_list(self, presform_list):
        pass

    def del_presform_list(self):
        pass

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
        big_list = self.original + self.premis + self.presform
        for n_thing in big_list:
            if isinstance(n_thing, LDRItem):
                pass
            else:
                return False
        return Structure._validate()

    property(get_original_list, set_original_list, del_original_list)
    property(get_premis_list, set_premis_list, del_premis_list)
    property(get_technicalmetadata_list, set_technicalmetadata_list,
             del_technicalmetadata_list)
    property(get_presform_list, set_presform_list, del_presform_list)
