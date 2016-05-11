
from os import makedirs
from os.path import abspath, dirname, exists, join, relpath
from sys import stderr

from .abc.abc.serializationwriter import SerializationWriter
from .abc.structure import Structure
from .ldritemoperations import copy, get_archivable_identifier,\
    pairtree_a_string
from .ldrpath import LDRPath
from .stage import Stage

__author__ = "Tyler Danstrom"
__email__ = " tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemArchiveStructureWriter(SerializationWriter):
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
        self.origin_root = origin_loc
        self.archive = archive_loc

    def write(self):
        """
        write the structure to disk
        """
        if self.structure.validate() and isinstance(self.structure, Stage):
            final_id = get_archivable_identifier()
            new_location = join(self.archive, final_id)
            new_object_parts = pairtree_a_string(final_id)
            new_location = join(self.archive, *new_object_parts)
            makedirs(new_location, exist_ok=True)
            for n_segment in self.structure.segment_list:
                for n_msuite in n_segment.materialsuite_list:
                    if len(n_msuite.technicalmetadata_list) > 0 \
                       and n_msuite.premis is not None:
                        main_dest = LDRPath(join(new_location,
                                                 n_msuite.content.item_name))
                        new_dirs = join(new_location,
                                        dirname(n_msuite.content.item_name))
                        makedirs(new_dirs, exist_ok=True)
                        copy(n_msuite.content, main_dest, clobber=False)
                        for n_techmd in n_msuite.technicalmetadata_list:
                            tech_dest = LDRPath(join(new_location,
                                                     n_techmd.content.
                                                     item_name))
                            new_dirs = join(new_location, dirname(n_techmd.
                                                                  content.
                                                                  item_name))
                            makedirs(new_dirs, exist_ok=True)
                            copy(n_techmd.content, tech_dest, clobber=False)

                        for n_presform in n_msuite.presform_list:
                            presform_dest = LDRPath(join(new_location,
                                                         n_presform.content.
                                                         item_name))
                            new_dirs = join(new_location, dirname(n_presform.
                                                                  content.
                                                                  item_name))
                            makedirs(new_dirs, exist_ok=True)
                            copy(n_presform.content, presform_dest)
                    else:
                        raise ValueError("cannot archive an incomplete " +
                                         "stage directory")

        else:
            stderr.write("invalid staging directory passed to  the " +
                         " file system archive structure writer")

    def get_structure(self):
        return self._structure

    def set_structure(self, value):
        if isinstance(value, Structure):
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

    structure = property(get_structure, set_structure)
    archive_loc = property(get_archive_loc, set_archive_loc)
