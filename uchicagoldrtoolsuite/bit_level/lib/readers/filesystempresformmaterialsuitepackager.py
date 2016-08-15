from os import scandir
from os.path import join, dirname, basename, isfile, splitext
from re import compile as re_compile

from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from .abc.presformmaterialsuitepackager import PresformMaterialSuitePackager
from ..ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class FileSystemPresformMaterialSuitePackager(PresformMaterialSuitePackager):
    """
    Reads a file system MaterialSuite serialization and knows how to package
    material suites from the contents for inclusion in segment structures
    """
    def __init__(self, stage_env_path, stage_id, label_text, label_number,
                 rel_content_path):
        """
        spawn a packager

        __Args__

        1. stage_env_path (str): The file system path to the staging environment
        2. stage_id (str): The stage identifier for the stage on disk
        3. label_text (str): The text that makes up the first part of the
            segment identifier
        4. label_number (int): The number that makes up the second part of
            the segment identifier
        5. rel_content_path (str): The **relative** path to the content in
            the segment which should have some of the parts of a MaterialSuite
        """
        log.debug("FileSystemMaterialSuitePackager spawned." +
                  "stage_env_path = {}, ".format(stage_env_path) +
                  "stage_id = {}, ".format(stage_id) +
                  "label_text = {}, ".format(label_text) +
                  "label_number = {}, ".format(str(label_number)) +
                  "rel_content_path = {}".format(rel_content_path))
        super().__init__()
        self.stage_env_path = stage_env_path
        self.stage_id = stage_id
        self.label_text = label_text
        self.label_number = label_number
        self.set_implementation('file system')
        self.rel_content_path = rel_content_path
        stage_fullpath = join(stage_env_path, stage_id)
        self.data_fullpath = join(stage_fullpath, 'data',
                                  label_text + "-" + str(label_number))
        log.debug("Computed data_fullpath = {}".format(self.data_fullpath))
        self.file_fullpath = join(self.data_fullpath, self.rel_content_path)
        log.debug("Computed file_fullpath = {}".format(self.file_fullpath))
        self.file_name = basename(self.rel_content_path)
        log.debug("Computed file_name = {}".format(self.file_name))
        self.admin_fullpath = join(stage_fullpath, 'admin',
                                   label_text + "-" + str(label_number))
        log.debug("Computed admin_fullpath = {}".format(self.admin_fullpath))

    def get_content(self):
        """
        Grab the content from the provided file path - content isn't optional
        and so the case of it not existing isn't handled. If there's no
        actual file on disk there it becomes a blank LDRPath pointed to that
        location.
        """
        log.debug("Retrieving content from provided information")
        return LDRPath(self.file_fullpath,
                       root=self.data_fullpath)

    def get_techmd_list(self):
        """
        Gather up the technical metadata files for the content path.

        Currently only looks for and packages .fits files
        """
        log.debug("Searching for techmd from provided information")
        fits_path = join(self.admin_fullpath,
                         "TECHMD",
                         self.rel_content_path+".fits.xml")
        if isfile(fits_path):
            log.debug("techmd found @ {}".format(fits_path))
            return [
                LDRPath(fits_path, root=join(self.admin_fullpath, "TECHMD"))
            ]
        log.debug("techmd not found @ {}".format(fits_path))
        return None

    def get_presform_list(self):
        """
        Grab all the presforms for the content path

        They should be in the same dir and match the presform_filename_pattern

        If any presforms are found they need to be packaged themselves, so
        fire up a presform material suite packager and feed it the relevant
        info.
        """
        presforms = []
        presform_filename_pattern = re_compile(
            "^{}\.presform(\.[a-zA-Z0-9]*)?$".format(
                self.file_name
            )
        )
        containing_folder_path = join(self.data_fullpath,
                                      dirname(self.rel_content_path))
        log.debug("Searching for presforms in {}".format(
            containing_folder_path)
        )
        siblings = [x.name for x in scandir(containing_folder_path)]
        for x in siblings:
            if presform_filename_pattern.match(x):
                log.debug("Presform found @ {}".format(x))
                presforms.append(
                    FileSystemPresformMaterialSuitePackager(
                        self.stage_env_path,
                        self.stage_id,
                        self.label_text,
                        self.label_number,
                        join(containing_folder_path, x)
                    ).package()
                )
        if len(presforms) > 0:
            return presforms
        log.debug("No presforms found")
        return None

    def get_premis(self):
        """
        Search for the premis record associated with the content
        """
        premis_path = join(self.admin_fullpath,
                           "PREMIS",
                           self.rel_content_path+".premis.xml")
        log.debug("Looking for PREMIS at {}".format(premis_path))
        premis_path = join(self.admin_fullpath,
                           "PREMIS",
                           self.rel_content_path+".premis.xml")
        if isfile(premis_path):
            log.debug("PREMIS found @ {}".format(premis_path))
            return LDRPath(premis_path,
                           root=join(self.admin_fullpath, "PREMIS"))
        log.debug("PREMIS not found @ {}".format(premis_path))
        return None

    def get_extension(self):
        log.debug("Trying to detect extension of {}").format(
            self.rel_content_path)
        ext = splitext(self.rel_content_path)[1]
        log.debug("Detected extension is: {}".format(str(ext)))
        return ext
