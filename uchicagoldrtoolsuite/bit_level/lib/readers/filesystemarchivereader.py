from os import scandir
from os.path import join, isdir, relpath
from logging import getLogger
from pathlib import Path

from pypairtree.utils import identifier_to_path, path_to_identifier

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success, recursive_scandir
from .filesystemmaterialsuitereader import FileSystemMaterialSuiteReader
from .abc.archiveserializationreader import ArchiveSerializationReader
from ..ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class FileSystemArchiveReader(ArchiveSerializationReader):
    """
    The reader for pairtree based FileSystem archive structure serializations

    Given the location of a long term storage environment and the identifier
    of an archive structure reconstructs the archive structure from byte
    streams serialized as files on disk.
    """
    @log_aware(log)
    def __init__(
        self, root, target_identifier, encapsulation="arf",
        materialsuite_deserializer=FileSystemMaterialSuiteReader,
        materialsuite_deserializer_kwargs={}
    ):
        """
        Create a new FileSystemArchiveReader

        __Args__

        1. root (str): The file system path to the long term storage env
        2. target_identifier (str): The identifier of an archive structure
            stored in the given long term storage environment

        __KWArgs__

        * encapsulation (str): A string to use to encapsulation the pairtree
            objects
        * materialsuite_deserializer (.abc.MaterialSuiteSerializerionReader):
            The materialsuite reader class to delegate handling of the
            MaterialSuite reads to.
        * materialsuite_deserializer_kwargs (dict): Any kwargs to be forwarded
            to the materialsuite deserializing class. Encapsulation is inherited
            automatically, unless otherwise specified
        """
        log_init_attempt(self, log, locals())
        super().__init__(root, target_identifier, materialsuite_deserializer,
                         materialsuite_deserializer_kwargs)
        self.encapsulation = encapsulation
        # If the ms deserializer needs encapsulation inherit it if none is
        # provided
        if 'encapsulation' not in self.materialsuite_deserializer_kwargs.keys():
            self.materialsuite_deserializer_kwargs['encapsulation'] = \
                self.encapsulation
        log_init_success(self, log)

    def _read_skeleton(self, lts_path=None, identifier=None):
        if lts_path is None:
            lts_path = self.root
        if identifier is None:
            identifier = self.target_identifier
        arch_root = join(lts_path, str(identifier_to_path(identifier)),
                         self.encapsulation)
        log.debug("Computed archive location: {}".format(arch_root))
        pairtree_root = join(arch_root, "pairtree_root")
        admin_root = join(arch_root, "admin")
        if not isdir(arch_root):
            raise ValueError("No such identifier ({}) ".format(identifier) +
                             "storage environment ({})!".format(lts_path))
        if not isdir(pairtree_root):
            raise ValueError("No pairtree root in Archive ({})!".format(
                identifier))
        if not isdir(admin_root):
            raise ValueError("No admin directory in Archive ({})!".format(
                identifier))

        accrec_dir_path = join(admin_root, "accession_records")
        adminnotes_path = join(admin_root, "adminnotes")
        legalnotes_path = join(admin_root, "legalnotes")

        if not isdir(accrec_dir_path):
            raise ValueError("No accession record subdir")
        if not isdir(adminnotes_path):
            raise ValueError("No adminnotes subdir")
        if not isdir(legalnotes_path):
            raise ValueError("No legalnotes subdir")

        log.info("Archive skeleton read/located")
        return arch_root, pairtree_root, admin_root, \
            accrec_dir_path, adminnotes_path, \
            legalnotes_path

    @log_aware(log)
    def _read_data(self, pairtree_root):
        for x in (x for x in recursive_scandir(pairtree_root) if
                  x.name == "premis.xml"):
            identifier = path_to_identifier(Path(x.path).parent.parent,
                                            root=Path(pairtree_root))
            self.struct.add_materialsuite(
                self.materialsuite_deserializer(
                    pairtree_root, identifier,
                    **self.materialsuite_deserializer_kwargs
                ).read()
            )

    @log_aware(log)
    def _read_admin(self, accrec_dir_path, adminnotes_path,
                    legalnotes_path, admin_root):
        log.info("Reading the administrative data from disk")
        log.debug("Reading accession records")
        for x in scandir(accrec_dir_path):
            accrec = LDRPath(x.path)
            accrec.item_name = relpath(x.path, accrec_dir_path)
            self.get_struct().add_accessionrecord(accrec)
        log.debug("Reading adminnotes")
        for x in scandir(adminnotes_path):
            adminnote = LDRPath(x.path)
            adminnote.item_name = relpath(x.path, adminnotes_path)
            self.get_struct().add_adminnote(adminnote)
        log.debug("Reading legalnotes")
        for x in scandir(legalnotes_path):
            legalnote = LDRPath(x.path)
            legalnote.item_name = relpath(x.path, legalnotes_path)
            self.get_struct().add_legalnote(legalnote)

    @log_aware(log)
    def read(self):
        """
        Reads the structure at the given location with the given identifier

        __Returns__

        self.struct (Archive): The archive structure
        """
        log.info("Reading Archive from disk serialization")
        arch_root, pairtree_root, admin_root, \
            accrec_dir_path, adminnotes_path, \
            legalnotes_path = self._read_skeleton()

        self._read_data(pairtree_root)

        self._read_admin(accrec_dir_path, adminnotes_path,
                         legalnotes_path, admin_root)
        log.debug("Read complete")
        return self.get_struct()
