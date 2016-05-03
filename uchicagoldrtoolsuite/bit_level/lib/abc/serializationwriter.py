from abc import ABCMeta, abstractmethod

class SerializationWriter(metaclass=ABCMeta):
    @abstractmethod
    def write(self):
        pass
