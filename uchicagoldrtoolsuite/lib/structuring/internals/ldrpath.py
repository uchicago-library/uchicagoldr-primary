'''
Created on Apr 14, 2016

@author: tdanstrom
'''

from pathlib import Path
from ..abc.ldritem import LDRItem
from abc import abstractmethod

class LDRPath(LDRItem):

    def __init__(self, param1):
        self.name = param1
        self.path = Path(self.name)
    
    @abstractmethod
    def open(self):
        LDRItem.open(self)
        
    def close(self):
        LDRItem.close(self)
      
    @abstractmethod
    def write(self):
        LDRItem.write(self)
        
    @abstractmethod
    def read(self):
        LDRItem.read(self)
    
    @abstractmethod
    def exists(self):
        LDRItem.exists(self)
        
    def is_flo(self):
        return self.is_flo  