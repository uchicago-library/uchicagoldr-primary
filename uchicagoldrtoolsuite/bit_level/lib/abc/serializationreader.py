from abc import ABCMeta, abstractmethod

'''
Created on Apr 13, 2016

@author: tdanstrom
'''


class SerializationReader(metaclass=ABCMeta):
    @abstractmethod
    def read(self, aStructure, aString):
        pass
