
from abc import ABCMeta, abstractproperty, abstractmethod


class Transformer(metaclass=ABCMeta):

    @abstractmethod
    def transform():
        pass

    def get_origin_structure(self):
        return self._origin_structure

    def set_origin_structure(self, value):
        self._origin_structure = value

    def get_destination_structure(self):
        return self._destination_structure

    def set_destination_structure(self, value):
        self._destination_structure = value

    origin_structure = abstractproperty(get_origin_structure,
                                        set_origin_structure)
    destination_structure = abstractproperty(get_destination_structure,
                                             set_destination_structure)
