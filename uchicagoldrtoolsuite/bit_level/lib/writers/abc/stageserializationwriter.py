from abc import ABCMeta, abstractmethod
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from .abc.serializationwriter import SerializationWriter


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class StageSerializationWriter(SerializationWriter, metaclass=ABCMeta):
    """
    A base class for all Staging Structure Serialization Writers
    """
    @abstractmethod
    @log_aware(log)
    def __init__(self, struct):
        """
        teeny helper init

        __Args__

        1. struct (Stage): The stage to write
        """
        log.debug("Entering the ABC init")
        self.set_struct(struct)
        log.debug("Exiting the ABC init")
