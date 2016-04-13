'''
Created on Apr 13, 2016

@author: tdanstrom
'''

from .abc.structure import Structure
from .abc.ldritem import LDRItem
from lib.structuring.materialsuite import MaterialSuiteStructure

class ArchiveStructure(Structure):

    def __init__(self, param1):
        self.requird_parts = ['identifier', 'segment', 'accessionrecord', 'admninnote', 'legalnote']
        self.identifier = param1
        self.segment = []
        self.accessionrecord = []
        self.adminnote = []
        self.legalnote = []
        
    def validate(self):
        super(ArchiveStructure, self)._validate()
        big_list = self.accessionrecord + self.adminnote + self.legalnote
        for n_thing in big_list:
            if getattr(n_thing, LDRItem):
                return False
        for n_thing in self.segment:
            if not getattr(n_thing, MaterialSuiteStructure):
                return False
        return True