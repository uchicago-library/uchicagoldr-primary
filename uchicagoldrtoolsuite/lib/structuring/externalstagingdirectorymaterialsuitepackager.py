
from .stagingmaterialsuitepackager import StagingMaterialSuitePackager
from .materialsuite import MaterialSuiteStructure

class ExternalStagingDirectoryMaterialSuitePackager(StagingMaterialSuitePackager):
    def __init__(self):
        self.struct_type = 'staging'
        self.implementation = 'directory'


    def package(self, an_item):
        msuite = MaterialSuiteStructure()
        msuite.original.append(an_item)
        return msuite
    
