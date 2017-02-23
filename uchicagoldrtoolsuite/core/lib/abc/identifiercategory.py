from abc import ABCMeta, abstractmethod, abstractproperty

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class IdentifierCategory(metaclass=ABCMeta):
    """The IdentifierCategory is an abstract for a category of identifier
    It has two abstract methods

    1. generate : meant to create a identifier value somehow
    2. show : meant to return the cateogyr and identifier value in some
    machine interpretable data structure
    """

    def get_value(self):
        """return the identifer value
        """
        return self._value

    def set_value(self, value):
        """set the identifier value
        """
        self._value = value

    @abstractmethod
    def generate():
        """a method to create an identifier value
        """
        pass

    @abstractmethod
    def show():
        """a method to return the cateory and value of an identifier in some machine
        interpretable format
        """
        pass

    value = abstractproperty(get_value, set_value)
