from abc import abstractmethod, ABCMeta
from logging import getLogger
from tempfile import TemporaryDirectory
from uuid import uuid4
from os.path import join

from pypremis.lib import PremisRecord

from uchicagoldrtoolsuite import log_aware
from .abc.packager import Packager
from ...structures.materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class MaterialSuitePackager(Packager, metaclass=ABCMeta):
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
        """
        # TODO: make this use ldritem_to_premisrecord
        with TemporaryDirectory() as tmp_dir:
            tmp_file_name = uuid4().hex
            tmp_file_path = join(tmp_dir, tmp_file_name)
            with premis_ldritem.open('rb') as f:
                with open(tmp_file_path, 'wb') as tmp_file:
                    tmp_file.write(f.read())
            premis = PremisRecord(frompath=tmp_file_path)
            ident = premis.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierValue()
        return ident

    @log_aware(log)
    def package(self):
        """
        default package implementation
        """
        log.debug("Packaging")

        try:
            premis = self.get_premis()
            if not premis:
                raise ValueError()
            self.struct.identifier = self.get_identifier(premis)
            self.struct.premis = premis
        except NotImplementedError:
            raise ValueError()


        try:
            content = self.get_content()
            if content:
                self.struct.set_content(content)
        except NotImplementedError:
            pass

        try:
            techmd_list = self.get_techmd_list()
            if techmd_list:
                self.struct.set_technicalmetadata_list(techmd_list)
        except NotImplementedError:
            pass
        log.debug("Packaging complete")
        return self.struct
