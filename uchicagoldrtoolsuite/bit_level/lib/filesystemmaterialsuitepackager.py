from .abc.materialsuitepackager import MaterialSuitePackager
from .materialsuite import MaterialSuite


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemMaterialSuitePackager(MaterialSuitePackager):
    """
    Reads a file system MaterialSuite serialization and knows how to package
    material suites from the contents for inclusion in segment structures
    """
    def __init__(self, stage_env_path, stage_id, label_text, label_number, orig_path):
        super().__init__()
        self.set_implementation('file system')
        self.stage_env_path = stage_env_path
        self.stage_id = stage_id
        self.label_text = label_text
        self.label_number = label_number
        self.orig_path = orig_path

    def package(self):
        msuite = MaterialSuite(an_item)
        msuite.original.append(an_item)
        return msuite

    def get_original(self):
        return LDRPath(self.orig_path)

    def get_techmd(self):
        pass

    def get_presform(self):
        pass

    def get_premis(self):
        pass
