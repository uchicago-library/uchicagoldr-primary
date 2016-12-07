from abc import abstractmethod, ABCMeta
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from .abc.serializationreader import SerializationReader
from ...structures.materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class MaterialSuiteSerializationReader(SerializationReader, metaclass=ABCMeta):
    """
    ABC for all MaterialSuitePackagers

    mandates:
        * .get_original()
        * .get_premis()
        * .get_techmd_list()

    all of which should return LDRItem subclasses or iters of them, if list
    is specified in the method name.
    If an implementation doesn't implement any of these by choice it should
    raise a NotImplementedError. The default .package() implementation
    simply eats these.
    """
    @abstractmethod
    @log_aware(log)
    def __init__(self, root, target_identifier):
        # TODO: The init here is slightly different from the StageReader init,
        # which sets the identifier to a uuid4(), this is due to a difference in
        # the underlying structures themselves - Stage's init require an
        # identifier. This should probably be made consistant, one way or
        # another.
        """
        helper init that sets the objects struct property
        """
        log.debug("Entering the ABC init")
        super().__init__(root, target_identifier)
        self.struct = MaterialSuite(self.target_identifier)
        log.debug("Exciting the ABC init")

    @abstractmethod
    def get_content(self):
        pass

    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod
    def get_techmd_list(self):
        pass

    @log_aware(log)
    def read(self):
        """
        default package implementation


        __Returns__

        * self.struct (MaterialSuite): The packaged MaterialSuite
        """
        log.info("Packaging")

        log.debug("Packaging PREMIS")
        try:
            self.struct.premis = self.get_premis()
        except NotImplementedError:
            raise ValueError('No PREMIS supplied by the reader')
        log.debug("PREMIS added to MaterialSuite")

        log.debug("Packaging content")
        try:
            content = self.get_content()
            if content:
                log.debug("Content located")
                self.struct.set_content(content)
            else:
                log.debug("No content located")
        except NotImplementedError:
            log.debug("Reader does not implement get_content()")

        log.debug("Packaing technical metadata")
        try:
            techmd_list = self.get_techmd_list()
            if techmd_list:
                log.debug("Technical metadata located")
                self.struct.set_technicalmetadata_list(techmd_list)
            else:
                log.debug("No technical metadata located")
        except NotImplementedError:
            log.debug("Reader does not implement get_techmd_list()")
        log.info("Packaging complete")
        return self.struct
