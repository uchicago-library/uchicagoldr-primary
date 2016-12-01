from abc import ABCMeta, abstractmethod
from logging import getLogger

from uchicagoldrtoolsuite import log_aware


__author__ = "Tyler Danstrom"
__email__ = "tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class Structure(metaclass=ABCMeta):
    """
    ABC for all Structures.

    Mandates the presence of a required parts str array and a str identifier

    Provides a low level _validate() method for assuring a structure is composed
    of the parts it promises.
    """

    required_parts = []

    @abstractmethod
    @log_aware(log)
    def validate(self):
        log.debug("Entering ABC validate()")
        for thing in self.get_required_parts():
            if getattr(self, thing, None) == None:
                return (False, "missing rec part: {}".format(thing))
        log.debug("Exiting ABC validate()")
        return True

    @log_aware(log)
    def get_required_parts(self):
        return self.required_parts

    required_parts = property(get_required_parts)
