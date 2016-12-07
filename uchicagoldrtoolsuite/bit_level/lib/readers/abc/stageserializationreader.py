from abc import ABCMeta, abstractmethod
from logging import getLogger
from inspect import getmro

from uchicagoldrtoolsuite import log_aware
from .materialsuiteserializationreader import MaterialSuiteSerializationReader
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
    @abstractmethod
    @log_aware(log)
    def __init__(self, root, target_identifier, materialsuite_deserializer):
        log.debug("Entering the ABC init")
        super().__init__(root, target_identifier)
        self.materialsuite_deserializer = materialsuite_deserializer
        self.struct = Stage(self.target_identifier)
        log.debug("Exiting the ABC init")

    def set_struct(self, x):
        if not isinstance(x, Stage):
            raise TypeError(
                "{} is a {}, not a {}".format(
                    str(x), str(type(x)), str(Stage)
                )
            )
        self._struct = x

    def get_materialsuite_deserializer(self):
        return self._materialsuite_deserializer

    def set_materialsuite_deserializer(self, x):
        if MaterialSuiteSerializationReader not in getmro(x):
            raise TypeError()
        self._materialsuite_deserializer = x

    materialsuite_deserializer = property(get_materialsuite_deserializer,
                                          set_materialsuite_deserializer)
