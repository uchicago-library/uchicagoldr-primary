from abc import abstractmethod, ABCMeta
from logging import getLogger
from tempfile import TemporaryDirectory
from uuid import uuid4
from os.path import join

from pypremis.lib import PremisRecord

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
    def __init__(self):
        # TODO: The init here is slightly different from the StageReader init,
        # which sets the identifier to a uuid4(), this is due to a difference in
        # the underlying structures themselves - Stage's init require an
        # identifier. This should probably be made consistant, one way or
        # another.
        """
        helper init that sets the objects struct property
        """
        log.debug("Entering the ABC init")
        self.struct = MaterialSuite()
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
    def get_identifier(self, premis_ldritem):
        """
        Instantiate the premis in a tempfile, read it, grab the identifier

        __Args__

        * premis_ldritem (LDRItem): an LDRItem with bytes for a PremisRecord
            serialization in it

        __Returns__

        * ident (str): The object identifier
        """
        # TODO: make this use ldritem_to_premisrecord
        log.debug("Computing identifier from PREMIS record")
        with TemporaryDirectory() as tmp_dir:
            tmp_file_name = uuid4().hex
            tmp_file_path = join(tmp_dir, tmp_file_name)
            with premis_ldritem.open('rb') as f:
                with open(tmp_file_path, 'wb') as tmp_file:
                    tmp_file.write(f.read())
            premis = PremisRecord(frompath=tmp_file_path)
            ident = premis.get_object_list()[0].get_objectIdentifier()[0].\
                get_objectIdentifierValue()
        log.debug("Computed identifier from PREMIS: {}".format(ident))
        return ident

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
            premis = self.get_premis()
            if not premis:
                raise ValueError()
            self.struct.identifier = self.get_identifier(premis)
            self.struct.premis = premis
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
