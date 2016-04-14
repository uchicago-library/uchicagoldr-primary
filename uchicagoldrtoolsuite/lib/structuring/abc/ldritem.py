'''
Created on Apr 13, 2016

@author: tdanstrom
'''

from abc import ABCMeta, abstractmethod, abstractproperty

class LDRItem(metaclass=ABCMeta):
    
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
    
    @abstractmethod(self):
    def is_flo(self):
        pass
    
    @abstractmethod
    def exists(self):
        pass
    
    def getname(self):
        return self._item_name
    
    def setname(self, value):
        if isinstance(value, str):
            self._item_name = value
        else:
            raise ValueError("item_name must be a string")
        
    def getisflo(self):
        return self._is_flo
    
    def setisflo(self, value):
        if isinstance(value, bool):
            self._is_flo = True
        else:
            raise ValueError("is_flo must be either True or False")

    def getpipe(self):
        return self._pipe
    
    def setpipe(self, value):
        self._pipe = value

    item_name = abstractproperty(getname, setname)
    pipe = abstractproperty(getpipe, setpipe)
    is_flo = abstractproperty(getisflo, setisflo)