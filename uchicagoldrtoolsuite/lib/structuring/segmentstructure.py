'''
Created on Apr 13, 2016

@author: tdanstrom
'''

from .abc.structure import Structure
from .materialsuite import MaterialSuiteStructure

class SegmentStructure(object):
    """The SegmentStructure holds materialsuites that are part of a segment of a larger structure. It validates to make sure that it only contains MaterialStructures
    1. label (str) 
    2. run (int)
    3. identifier (str): 
    4. required_parts (list):
    5. materialsuite (list): 
    """
    
    
    def __init__(self, param1, param2):
        self.label = param1
        self.run = param2
        self.identifier = param1 + param2
        self.required_parts = ['identifier', 'materialsuite', 'identifier']
        self.materialsuite = []

        
    def validate(self):
        for n_thing in self.materialsuite:
            if getattr(n_thing, MaterialSuiteStructure):
                pass
            else:
                return False
        return Structure._validate()
