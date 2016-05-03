from sys import stderr

from ..lib.abc.serializationwriter import SerializationWriter
from ..lib.abc.structure import Structure


class FileSystemArchiveStructureWriter(SerializationWriter):
    def __init__(self, aStructure):
        self.structure = aStructure

    def write(self):
        if self.structure.validate():
            pass
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

    structure = property(get_structure, set_structure)
