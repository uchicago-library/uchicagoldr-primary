
from os.path import exists
from sys import stderr

from uchicagoldrtoolsuite.core.lib.convenience import get_archivable_identifier

from .abc.abc.serializationwriter import SerializationWriter
from .abc.structure import Structure
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
    def __init__(self, aStructure, archive_loc):
        """
        initialize the writer

        __Args__

        1. aStructure (ArchiveStructure): The structure to write
        """
        self.structure = aStructure
        self.archive = archive_loc

    def write(self):
        """
        write the structure to disk
        """
        if self.structure.validate() and isinstance(self.structure, Stage):
            final_id = get_archivable_identifier()
            print(final_id)
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
