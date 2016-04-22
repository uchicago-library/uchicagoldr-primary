
from .stagingmaterialsuitepackager import StagingMaterialSuitePackager
from .materialsuite import MaterialSuiteStructure

class ExternalStagingDirectoryMaterialSuitePackager(StagingMaterialSuitePackager):
    def __init__(self):
        self.struct_type = 'staging'
        self.implementation = 'directory'


    def package(self, an_item):
        msuite = MaterialSuiteStructure(an_item)
        msuite.original.append(an_item)
        return msuite
    

    def get_techmd(self):
        pass

    def get_presform(self):
        pass

    def get_premis(self):
        pass

    def get_struct(self):
        return self._struct

    def set_struct(self, value):
        self._struct = value

    def set_type(self, value):
        self._struct_type = value

    def get_type(self):
        return self._struct_type

    def set_implementation(self, value):
        self._implementation = value

    def get_implementation(self):
        return self._implementation
    
    struct = property(get_struct, set_struct)
    struct_type = property(get_type, set_type)
    implementation = property(get_implementation, set_implementation)
