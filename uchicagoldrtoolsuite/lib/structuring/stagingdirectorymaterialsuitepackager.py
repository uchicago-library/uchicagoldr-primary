
class StagingDirectoryMaterialSuitePackager(StagingMaterialSuitePackager):
    def __init__(self):
        self.struct_type = 'staging'
        self.implementation = 'directory'


    def package(self):
        return []
