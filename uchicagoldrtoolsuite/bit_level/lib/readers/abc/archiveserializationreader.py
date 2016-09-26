from abc import ABCMeta, abstractmethod
from uuid import uuid1

from .abc.serializationreader import SerializationReader
from ...structures.archive import Archive


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class ArchiveSerializationReader(SerializationReader, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self.set_struct(Archive(str(uuid1())))
