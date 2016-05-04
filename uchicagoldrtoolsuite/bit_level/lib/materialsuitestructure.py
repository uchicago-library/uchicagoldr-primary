from .abc.structure import Structure
from .abc.ldritem import LDRItem


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class MaterialSuiteStructure(Structure):
    def __init__(self, param1):
        self.required_parts = ['identifier', 'original', 'premis',
                               'technicalmetadata', 'presform']
        self.identifier = param1
        self.original = []
        self.premis = []
        self.technicalmetadata = []
        self.presform = []

    def validate(self):
        big_list = self.original + self.premis + self.presform
        for n_thing in big_list:
            if isinstance(n_thing, LDRItem):
                pass
            else:
                return False
        return Structure._validate()
