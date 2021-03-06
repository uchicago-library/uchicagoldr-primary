from abc import ABCMeta, abstractmethod
from logging import getLogger
from inspect import getmro

from uchicagoldrtoolsuite import log_aware
from .abc.serializationwriter import SerializationWriter
from .materialsuiteserializationwriter import MaterialSuiteSerializationWriter
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
    def __init__(self, struct, root, materialsuite_serializer,
                 eq_detect="bytes", materialsuite_serializer_kwargs={}):
        """
        another teeny helper init

        __Args__

        1. struct (Archive): the archive to write
        """
        log.debug("Entering the ABC init")
        super().__init__(struct, root, eq_detect=eq_detect)
        self._materialsuite_serializer = None
        self.materialsuite_serializer = materialsuite_serializer
        if 'eq_detect' not in materialsuite_serializer_kwargs.keys():
            materialsuite_serializer_kwargs['eq_detect'] = self.eq_detect
        self.materialsuite_serializer_kwargs = materialsuite_serializer_kwargs
        log.debug("Exiting the ABC init")

    @log_aware(log)
    def set_struct(self, struct):
        if not isinstance(struct, Archive):
            raise TypeError(
                "{} is a {} not a {}".format(
                    str(struct), str(type(struct)), str(Archive)
                )
            )
        self._struct = struct

    @log_aware(log)
    def get_materialsuite_serializer(self):
        return self._materialsuite_serializer

    @log_aware(log)
    def set_materialsuite_serializer(self, x):
        # The ABCMeta metaclass weirdly breaks using isinstance() here, as well
        # as getclasstree(), so though examining the MRO is a bit crazy, I guess
        # it's what I have to go with
        if MaterialSuiteSerializationWriter not in getmro(x):
            raise TypeError(
                "{} is a {}, not a {}".format(
                    str(x), str(type(x)), str(MaterialSuiteSerializationWriter)
                )
            )
        self._materialsuite_serializer = x

    @log_aware(log)
    def get_materialsuite_serializer_kwargs(self):
        return self._materialsuite_serializer_kwargs

    @log_aware(log)
    def set_materialsuite_serializer_kwargs(self, x):
        if not isinstance(x, dict):
            raise TypeError()
        self._materialsuite_serializer_kwargs = x

    materialsuite_serializer = property(get_materialsuite_serializer,
                                        set_materialsuite_serializer)
    materialsuite_serializer_kwargs = property(
        get_materialsuite_serializer_kwargs,
        set_materialsuite_serializer_kwargs
    )
