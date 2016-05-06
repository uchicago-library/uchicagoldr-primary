from os.path import join

from .abc.materialsuitepackager import MaterialSuitePackager
from .ldrpath import LDRPath


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
    def __init__(self, stage_env_path, stage_id, label_text, label_number,
                 rel_orig_path):
        super().__init__()
        self.set_implementation('file system')
        self.rel_orig_path = rel_orig_path
        stage_fullpath = join(stage_env_path, stage_id)
        self.data_fullpath = join(stage_fullpath, 'data',
                                  label_text + "-" + str(label_number))
        self.admin_fullpath = join(stage_fullpath, 'admin',
                                  label_text + "-" + str(label_number))

    def get_original_list(self):
        return [LDRPath(join(self.data_fullpath, self.rel_orig_path),
                        root=self.data_fullpath)]

    def get_techmd_list(self):
        raise NotImplementedError()

    def get_presform_list(self):
        raise NotImplementedError()

    def get_premis_list(self):
        raise NotImplementedError()
