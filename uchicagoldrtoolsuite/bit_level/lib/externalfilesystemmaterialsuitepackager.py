from .abc.materialsuitepackager import MaterialSuitePackager
from .ldrpath import LDRPath


class ExternalFileSystemMaterialSuitePackager(MaterialSuitePackager):
    def __init__(self, orig, root=None):
        super().__init__()
        self.orig = orig
        self.root = root

    def get_original_list(self):
        return [LDRPath(self.orig, root=self.root)]

    def get_premis_list(self):
        raise NotImplementedError()

    def get_techmd_list(self):
        raise NotImplementedError()

    def get_presform_list(self):
        raise NotImplementedError()
