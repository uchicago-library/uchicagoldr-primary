'''
Created on Apr 13, 2016

@author: tdanstrom
'''
from abc import ABCMeta, abstractmethod

class SerializationReader:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def read(self, aStructure, aString):
        pass