'''
Created on Apr 13, 2016

@author: tdanstrom
'''

from abc import ABCMeta, abstractmethod, abstractproperty
from pathlib import Path

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
    
    def getpath(self):
        return self._path
    
    def setpath(self, value):
        self._path = Path(value)
    
    def getisflo(self):
        return self._is_flo
    
    def setisflo(self, value):
        self._is_flo = True

    def getpipe(self):
        return self._pipe
    
    def setpipe(self):
        self._pipe = None

    item_name = abstractproperty(getname, setname)
    path = abstractproperty(getpath, setpath)
    pipe = abstractproperty(getpipe, setpipe)
    is_flo = abstractproperty(getisflo, setisflo)