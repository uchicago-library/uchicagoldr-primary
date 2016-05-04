from abc import ABCMeta, abstractmethod

from .abc.serializationwriter import SerializationWriter
from ..stage import Stage


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class StageSerializationWriter(SerializationWriter, metaclass=ABCMeta):
    """
    A base class for all Staging Structure Serialization Writers
    """
    @abstractmethod
    def __init__(self):
        self.set_struct(Stage)
