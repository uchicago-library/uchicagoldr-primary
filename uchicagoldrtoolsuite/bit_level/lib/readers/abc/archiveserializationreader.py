from abc import ABCMeta, abstractmethod
from logging import getLogger
from inspect import getmro

from uchicagoldrtoolsuite import log_aware
from .materialsuiteserializationreader import MaterialSuiteSerializationReader
from .abc.serializationreader import SerializationReader
from ...structures.archive import Archive


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class ArchiveSerializationReader(SerializationReader, metaclass=ABCMeta):
    """
    The ABC for Archive serialization readers

    implements a helper init
    """
    @abstractmethod
    @log_aware(log)
    def __init__(self, root, target_identifier, materialsuite_deserializer):
        log.debug("Entering the ABC init")
        super().__init__(root, target_identifier)
        self.struct = Archive(self.target_identifier)
        self.materialsuite_deserializer = materialsuite_deserializer
        log.debug("Exiting the ABC init")

    @log_aware(log)
    def set_struct(self, struct):
        if not isinstance(struct, Archive):
            raise TypeError(
                "{} is a {}, not an {}".format(
                    str(struct), str(type(struct)), str(Archive)
                )
            )
        self._struct = struct

    def get_materialsuite_deserializer(self):
        return self._materialsuite_deserializer

    def set_materialsuite_deserializer(self, x):
        if MaterialSuiteSerializationReader not in getmro(x):
            raise TypeError()
        self._materialsuite_deserializer = x

    materialsuite_deserializer = property(get_materialsuite_deserializer,
                                          set_materialsuite_deserializer)
