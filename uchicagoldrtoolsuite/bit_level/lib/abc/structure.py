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

    _required_parts = []

    @abstractmethod
    def validate(self):
        for thing in self.get_required_parts():
            if  getattr(self, thing, None) == None:
                print("333333333333")
                print(thing)
                return False
        return True

    def get_required_parts(self):
        return self._required_parts

    def set_required_parts(self, required_parts):
        for x in required_parts:
            self.add_required_part(x)

    def del_required_parts(self):
        while self.get_required_parts():
            self._required_parts.pop()

    def add_required_part(self, x):
        if not isinstance(x, str):
            raise ValueError('Required parts must be specified as strings.')
        self._required_parts.append(x)

    required_parts = property(get_required_parts, set_required_parts)
