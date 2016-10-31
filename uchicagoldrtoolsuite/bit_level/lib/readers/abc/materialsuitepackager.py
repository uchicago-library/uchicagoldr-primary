from abc import abstractmethod, ABCMeta
from tempfile import TemporaryDirectory
from uuid import uuid4
from os.path import join

from pypremis.lib import PremisRecord

from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from .abc.packager import Packager
from ...structures.materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class MaterialSuitePackager(Packager, metaclass=ABCMeta):
    """
    ABC for all MaterialSuitePackagers

    mandates:
        * .get_original()
        * .get_premis()
        * .get_techmd()
        * .get_presform()

    all of which should return iters of LDRItem subclasses
    if an implementation doesn't implement any of these by choice it should
    raise a NotImplementedError. The default .package() implementation
    simply eats these.
    """
    @abstractmethod
    def __init__(self):
        self.struct = MaterialSuite()

    @abstractmethod
    def get_content(self):
        pass

    @abstractmethod
    def get_premis(self):
        pass

    @abstractmethod
    def get_techmd_list(self):
        pass

    @abstractmethod
    def get_presform_list(self):
        pass

    def get_identifier(self, premis_ldritem):
        with TemporaryDirectory() as tmp_dir:
            tmp_file_name = uuid4().hex
            tmp_file_path = join(tmp_dir, tmp_file_name)
            with premis_ldritem.open('rb') as f:
                with open(tmp_file_path, 'wb') as tmp_file:
                    tmp_file.write(f.read())
            premis = PremisRecord(frompath=tmp_file_path)
            ident = premis.get_object_list()[0].get_objectIdentifier()[0].get_objectIdentifierValue()
        return ident

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
            presform_list = self.get_presform_list()
            if presform_list:
                self.struct.set_presform_list(presform_list)
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
