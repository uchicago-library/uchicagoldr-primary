'''
Created on Apr 13, 2016

@author: tdanstrom
'''

from abc import ABCMeta, abstractmethod, abstractproperty

class LDRItem:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def read(self):
        pass
    
    @abstractmethod
    def write(self):
        pass
    
    @abstractmethod
    def open(self):
        pass
    
    @abstractmethod
    def close(self):
        pass
    
    @abstractmethod
    def is_flo(self):
        return True
    
    @abstractmethod
    def exists(self):
        pass
    
    def getname(self):
        return self._item_name
    
    def setname(self, value):
        self._item_name = value
    
    item_name = abstractproperty(getname, setname)