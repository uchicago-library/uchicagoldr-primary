'''
Created on Apr 13, 2016

@author: tdanstrom
'''
from abc import ABCMeta, abstractmethod

class SerializationReader(metaclass=ABCMeta):
    
    @abstractmethod
    def read(self, aStructure, aString):
        pass