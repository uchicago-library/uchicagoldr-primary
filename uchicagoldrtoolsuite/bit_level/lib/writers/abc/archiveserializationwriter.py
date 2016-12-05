from abc import ABCMeta, abstractmethod
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from .abc.serializationwriter import SerializationWriter
from ...structures.archive import Archive


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class ArchiveSerializationWriter(SerializationWriter, metaclass=ABCMeta):
    """
    A base class for all Staging Structure Serialization Writers
    """
    @abstractmethod
    @log_aware(log)
    def __init__(self, struct):
        """
        another teeny helper init

        __Args__

        1. struct (Archive): the archive to write
        """
        log.debug("Entering the ABC init")
        self.set_struct(struct)
        log.debug("Exiting the ABC init")

    def set_struct(self, struct):
        if not isinstance(struct, Archive):
            raise ValueError(
                "{} is a {} not a {}".format(
                    str(struct), str(type(struct)), str(Archive)
                )
            )
        self._struct = struct

