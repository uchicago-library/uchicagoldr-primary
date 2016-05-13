
from os import makedirs
from os.path import abspath, dirname, exists, join, relpath
from sys import stderr

from .abc.abc.serializationwriter import SerializationWriter
from .ldritemoperations import copy, get_archivable_identifier,\
    pairtree_a_string
from .ldrpath import LDRPath
from .pairtree import Pairtree
from .stage import Stage

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemArchiveWriter(SerializationWriter):
    """
    writes an archive structure to the file system as a directory
    """
    def __init__(self, aStructure, archive_loc, origin_loc):
        """
        initialize the writer

        __Args__

        1. aStructure (StagingStructure): The structure to write
        2. archive_loc (str): the root directory for the archive of the ldr
        3. origin_loc (str): the root directory of the stage directory
        being archived
        """
        self.structure = aStructure
        self.identifier = get_archivable_identifier(noid=False)
        self.pairtree = Pairtree(self.identifier).get_pairtree_path()
        self.origin_root = origin_loc
        self.archive = archive_loc

    def find_and_pairtree_admin_content(self, segment_id, iterable):
        for n_thing in iterable:
            n_thing_destination = LDRPath(
                self.pairtree.pairtree_path,
                'admin', segment_id,
                n_thing.content.item_name)
            self.pairtree.content = n_thing_destination

    def find_and_pairtree_data_content(self, segment_id, n_thing):
        n_thing_destination = LDRPath(
            self.pairtree.pairtree_path,
            'data', segment_id,
            n_thing.content.item_name)
        self.pairtree.content = n_thing_destination

    def write(self):
        """
        serializes a staging directory structure into an archive structure
        onto disk
        """
        if self.structure.validate():
            for n_segment in self.structure.segment_list:
                segment_id = n_segment.label+str(n_segment.run)
                for n_msuite in n_segment.materialsuite_list:
                    self.find_and_pairtree_data_content(
                        segment_id, n_msuite.content)
                    self.find_and_pairtree_admin_content(
                        segment_id, n_msuite.technicalmetadata_list)
                    self.find_and_pairtree_admin_content(
                        segment_id, n_msuite.premis)
                    for n_presform_msuite in n_msuite.presform_list:
                        self.find_and_pairtree_data_content(
                            segment_id, n_presform_msuite.content)
                        self.find_and_pairtree_admin_content(
                            segment_id,
                            n_presform_msuite.technicalmetadata_list)
                        self.find_and_pairtree_admin_content(
                            segment_id, n_presform_msuite.premis)
            for n_item in self.pairtree:
                print(n_item)
        else:
            stderr.write("invalid staging directory passed to  the " +
                         " file system archive structure writer")

    def get_structure(self):
        return self._structure

    def set_structure(self, value):
        if isinstance(value, Stage):
            self._structure = value
        else:
            raise ValueError("must pass an instance of Structure" +
                             " abstract class to a " +
                             " FileSystemArchiveStructureWriter")

    def get_archive_loc(self):
        return self._archive_loc

    def set_archive_loc(self, value):
        if exists(value):
            self._archive_loc = value

        else:
            raise ValueError("Cannot pass {} to the archive".format(value) +
                             " writer because that path does not exist")

    def get_identifier(self):
        return self._identifier

    def set_identifier(self, value):
        self._identifier = value

    def get_pairtree(self):
        return self._pairtree

    def set_pairtree(self, value):
        self._pairtree = value

    def get_origin_root(self):
        return self._origin_root

    def set_origin_root(self, value):
        if not exists(value):
            raise ValueError("origin_root {}".format(self.origin_root) +
                             " in FileSystemArchiveWriter" +
                             " must exist on the file system")
        self._origin_root = value

    structure = property(get_structure, set_structure)
    identifier = property(get_identifier, set_identifier)
    pairtree = property(get_pairtree, set_pairtree)
    origin_root = property(get_origin_root, set_origin_root)
    archive_loc = property(get_archive_loc, set_archive_loc)
