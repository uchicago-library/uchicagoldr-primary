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
    @abstractmethod
    def validate(self):
        pass

    def _validate(self):
        for n_thing in self.required_parts:
            if  getattr(self, n_thing, None) == None:
                return False
            elif (n_thing != 'identifier' and not\
                  isinstance(getattr(self, n_thing, None), list)):
                return False
        return True

        def getrequiredparts(self):
            return self._required_parts

        def setrequiredparts(self, value):
            self._required_parts = value

        def getidentifier(self):
            return self._identifier

        def setidentifier(self, value):
            self._identifier = value

        required_parts = abstractproperty(getrequiredparts, setrequiredparts)
        identifier = abstractproperty(getidentifier, setidentifier)
