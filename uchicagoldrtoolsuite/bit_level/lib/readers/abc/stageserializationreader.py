from abc import ABCMeta, abstractmethod
from logging import getLogger
from uuid import uuid1

from uchicagoldrtoolsuite import log_aware
from .abc.serializationreader import SerializationReader
from ...structures.stage import Stage


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class StageSerializationReader(SerializationReader, metaclass=ABCMeta):
    """
    A base class for all Staging Structure Serialization Readers
    """

    _stage_id = None

    @abstractmethod
    @log_aware(log)
    def __init__(self):
        log.debug("Entering the ABC init")
        self.set_struct(Stage(str(uuid1())))
        log.debug("Exiting the ABC init")

    @log_aware(log)
    def get_stage_id(self):
        return self._stage_id

    @log_aware(log)
    def set_stage_id(self, value):
        self._stage_id = value

    stage_id = property(get_stage_id, set_stage_id)
