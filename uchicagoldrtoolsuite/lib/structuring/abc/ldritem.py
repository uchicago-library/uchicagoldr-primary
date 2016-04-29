'''
Created on Apr 13, 2016

@author: tdanstrom, balsamo
'''
from abc import ABCMeta, abstractmethod


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
    def exists(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def get_name(self):
        return self._item_name

    def set_name(self, value):
        if isinstance(value, str):
            self._item_name = value
        else:
            raise ValueError("item_name must be a string")

    def get_is_flo(self):
        return self.is_flo

    def set_is_flo(self, value):
        if isinstance(value, bool):
            self._is_flo = value
        else:
            raise ValueError("is_flo must be either True or False")

    item_name = property(get_name, set_name)
    is_flo = property(get_is_flo, set_is_flo)
