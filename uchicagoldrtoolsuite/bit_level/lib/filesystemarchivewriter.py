
from os import makedirs
from os.path import abspath, dirname, exists, join, relpath
from sys import stderr

from .abc.archiveserializationwriter import ArchiveSerializationWriter
from .archive import Archive
from .ldritemoperations import copy
from .ldrpath import LDRPath
from .pairtree import Pairtree
from .stage import Stage

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemArchiveWriter(ArchiveSerializationWriter):
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
        self.pairtree = Pairtree(self.structure.identifier).get_pairtree_path()
        self.origin_root = origin_loc
        self.archive_loc = archive_loc

    def pairtree_an_admin_content(self, segment_id, a_thing):
        return LDRPath(join(self.archive_loc, self.pairtree,
                            'admin', segment_id, a_thing.item_name))

    def pairtree_a_data_content(self, segment_id, a_thing):
        return LDRPath(join(self.archive_loc, self.pairtree,
                            'data', segment_id, a_thing.item_name))

    def find_and_pairtree_admin_content(self, segment_id,
                                        iterable):
        for n_thing in iterable:
            makedirs(join(self.archive_loc, self.pairtree,
                          'admin', segment_id, dirname(n_thing.item_name)),
                     exist_ok=True)
            n_thing_destination = self.pairtree_an_admin_content(segment_id,
                                                                 n_thing)
            copy(n_thing, n_thing_destination, False)

    def find_and_pairtree_data_content(self, segment_id, n_thing):
        makedirs(join(self.archive_loc, self.pairtree,
                      'data', segment_id, dirname(n_thing.item_name)),
                 exist_ok=True)
        n_thing_destination = self.pairtree_a_data_content(segment_id,
                                                           n_thing)
        copy(n_thing, n_thing_destination, False)

    def write(self):
        """
        serializes a staging directory structure into an archive structure
        onto disk
        """
        if self.structure.validate():
            makedirs(join(self.archive_loc,
                          self.pairtree), exist_ok=True)
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
        else:
            stderr.write("invalid archive structure instance passed to  the " +
                         " file system archive structure writer")

    def get_structure(self):
        return self._structure

    def set_structure(self, value):
        if isinstance(value, Archive):
            self._structure = value
        else:
            raise ValueError("must pass an instance of Structure" +
                             " abstract class to a " +
                             "FileSystemArchiveStructureWriter")

    def get_archive_loc(self):
        return self._archive_loc

    def set_archive_loc(self, value):
        if exists(value):
            self._archive_loc = value

        else:
            raise ValueError("Cannot pass {} to the archive".format(value) +
                             " writer because that path does not exist")

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
    pairtree = property(get_pairtree, set_pairtree)
    origin_root = property(get_origin_root, set_origin_root)
    archive_loc = property(get_archive_loc, set_archive_loc)
