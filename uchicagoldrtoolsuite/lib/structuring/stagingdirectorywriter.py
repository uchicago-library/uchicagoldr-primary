
from .abc.serializationwriter import SerializationWriter

class StagingDirectoryWriter(SerializationWriter):

    def __init__(self, aStructure):
        self.structure = aStructure

    def write(self):
        validated = self.structure.validate()
        print(validated)
        return validated

