from abc import ABCMeta, abstractproperty, abstractmethod
from logging import getLogger

from uchicagoldrtoolsuite import log_aware

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class Transformer(metaclass=ABCMeta):
    """The Transformer abstract class should be used as the base class for all
    transformer concrete classes

    The transformer's purpose is to take an instance of one type of Structure a
    and transform it into an instance of a different type of Structure.
    """
    @abstractmethod
    @log_aware(log)
    def transform():
        """should return an example of whatever Structure type needs to
        be the output

        The purpose of this method is implement the conversion process
        of making one type of Structure into another.
        """
        pass

    @log_aware(log)
    def get_origin_structure(self):
        """returns the origin structure instance or the original type of
        structure
        """
        return self._origin_structure

    @log_aware(log)
    def set_origin_structure(self, value):
        """sets the origin structure data attribute
        """
        self._origin_structure = value

    @log_aware(log)
    def get_destination_structure(self):
        """gets the destination structure or the type of structure that shold result
        from transformation
        """
        return self._destination_structure

    @log_aware(log)
    def set_destination_structure(self, value):
        """sets the destination structure or the type of structure that the origin
        structure needs to be converted to
        """
        self._destination_structure = value

    origin_structure = abstractproperty(get_origin_structure,
                                        set_origin_structure)
    destination_structure = abstractproperty(get_destination_structure,
                                             set_destination_structure)
