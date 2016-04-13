
from abc import ABCMeta, abstractmethod

class SerializationWriter:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def write(self):
        pass
    
    