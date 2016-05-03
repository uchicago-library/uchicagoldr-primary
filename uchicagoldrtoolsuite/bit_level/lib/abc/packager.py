
from abc import ABCMeta, abstractmethod, abstractproperty

class Packager(metaclass=ABCMeta):

    def set_struct(self, value):
        self._struct = value

    def get_struct(self):
        return self._struct

    def set_type(self, value):
        self._struct_type = value

    def get_type(self):
        return self._struct_type

    def set_implementation(self, value):
        return self._implementation

    def get_implementation(self, value):
        return self._implemetnation

    @abstractmethod
    def package(self):
        pass
    
    struct = abstractproperty(set_struct, get_struct)
    struct_type = abstractproperty(set_type, get_type)
    implementation = abstractproperty(set_implementation, get_implementation)
