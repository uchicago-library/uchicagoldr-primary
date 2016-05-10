from os import listdir
from os.path import join, dirname, basename, isfile
from re import compile as re_compile

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
        techmd = []
        fits_path = join(self.admin_fullpath,
                             "TECHMD",
                             self.rel_orig_path+".fits.xml")
        if isfile(fits_path):
            techmd.append(LDRPath(fits_path, root=join(self.admin_fullpath, "TECHMD")))
        return techmd

    def get_presform_list(self):
        presforms = []
        presform_filename_pattern = re_compile("^{}\.presform(\.[a-zA-Z0-9]*)?$".format(
            basename(self.rel_orig_path)
        ))
        containing_folder_path = join(self.data_fullpath,
                                      dirname(self.rel_orig_path))
        siblings = [x for x in listdir(containing_folder_path)]
        for x in siblings:
            if presform_filename_pattern.match(x):
                presforms.append(LDRPath(join(containing_folder_path, x),
                                         root=containing_folder_path))
        return presforms

    def get_premis_list(self):
        premis = []
        premis_path = join(self.admin_fullpath,
                           "PREMIS",
                           self.rel_orig_path+".premis.xml")
        if isfile(premis_path):
            premis.append(
                LDRPath(premis_path, root=join(self.admin_fullpath, "PREMIS"))
            )
        return premis
