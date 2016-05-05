from .abc.materialsuitepackager import MaterialSuitePackager
from .ldrpath import LDRPath


class ExternalFileSystemMaterialSuitePackager(MaterialSuitePackager):
    def __init__(self, orig):
        super().__init__(orig)

    def get_premis(self):
        raise NotImplementedError()

    def get_techmd(self):
        raise NotImplementedError()

    def get_presform(self):
        raise NotImplementedError()
