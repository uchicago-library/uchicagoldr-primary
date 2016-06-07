from abc import ABCMeta, abstractproperty, abstractmethod


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class Structure(metaclass=ABCMeta):
    """
    ABC for all Structures.

    Mandates the presence of a required parts str array and a str identifier

    Provides a low level _validate() method for assuring a structure is composed
    of the parts it promises.
    """

    required_parts = []

    @abstractmethod
    def validate(self):
        for thing in self.get_required_parts():
            if  getattr(self, thing, None) == None:
                return False
        return True

    def get_required_parts(self):
        return self.required_parts

    required_parts = property(get_required_parts)
