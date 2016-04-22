
from .abc.serializationwriter import SerializationWriter

class StagingDirectoryWriter(SerializationWriter):

    def __init__(self, aStructure):
        self.structure = aStructure

    def write(self, stage_directory):
        validated = self.structure.validate()
        if not validated:
            raise ValueError("Cannot serialize an invalid structure of type {}".\
                             format(type(self.structure).__name__))
        else:
            if not exists(stage_directory):
                mkdir(stage_directory)
            if not eixsts(join(stage_directory, 'data')):
                mkdir(join(stage_directory, 'data'))
            if not eixsts(join(stage_directory, 'admin')):
                mkdir(join(stage_directory, 'admin'))
                
            for n_item in self.structure.segment:
                
                print(n_item)

