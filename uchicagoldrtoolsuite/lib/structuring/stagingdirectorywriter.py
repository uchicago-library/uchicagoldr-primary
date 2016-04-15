
from .abc.serializationwriter import SerializationWriter

class StagingDirectoryWriter(SerializationWriter):

    def __init__(self, aStructure):
        self.structure = aStructure

    def write(self):
        validated = self.structure.validate()
        if not validated:
            raise ValueError("Cannot serialize an invalid structure of type {}".\
                             format(type(self.structure).__name__))
        else:
            for n_item in self.structure.segment:
                print(n_item)

