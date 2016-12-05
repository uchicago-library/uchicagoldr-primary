from abc import ABCMeta, abstractmethod
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from .abc.serializationwriter import SerializationWriter
from ...structures.materialsuite import MaterialSuite


log = getLogger(__name__)


class MaterialSuiteSerializationWriter(SerializationWriter, metaclass=ABCMeta):
    @abstractmethod
    @log_aware(log)
    def __init__(self, struct):
        self.struct = struct

    @log_aware(log)
    def set_struct(self, struct):
        if not isinstance(struct, MaterialSuite):
            raise ValueError(
                "{} is a {}, not a {}".format(
                    str(struct), str(type(struct)), str(MaterialSuite)
                )
            )
        self._struct = struct
