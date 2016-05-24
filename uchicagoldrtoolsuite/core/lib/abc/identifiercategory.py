from abc import ABCMeta, abstractmethod, abstractproperty


class IdentifierCategory(metaclass=ABCMeta):

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    @abstractmethod
    def generate():
        pass

    @abstractmethod
    def show():
        pass

    value = abstractproperty(get_value, set_value)
