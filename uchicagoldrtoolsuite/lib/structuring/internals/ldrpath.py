

from pathlib import Path
from ..abc.ldritem import LDRItem
from abc import abstractmethod

class LDRPath(LDRItem):

    def __init__(self, param1):
        self.item_name = param1
        self.path = Path(self.item_name)
    
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
