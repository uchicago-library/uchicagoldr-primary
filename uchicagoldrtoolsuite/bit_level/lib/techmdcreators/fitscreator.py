from os import makedirs
from os.path import join, dirname, isfile
from uuid import uuid4
from json import dumps
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.bash_cmd import BashCommand
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from ..ldritems.ldrpath import LDRPath
from ..ldritems.abc.ldritem import LDRItem
from ..ldritems.ldritemcopier import LDRItemCopier
from .abc.technicalmetadatacreator import TechnicalMetadataCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class FITsCreator(TechnicalMetadataCreator):
    # TODO: Technical metadata creators probably need a go over
    # like the converters
    """
    A TechnicalMetadataCreator which runs a local FITs instance against the
    content of a MaterialSuite in order to generate a technical metadata entry
    """
    @log_aware(log)
    def __init__(self, materialsuite, working_dir, timeout=None,
                 data_transfer_obj={}):
        """
        Creates a new FITsCreator

        __Args__

        1. materialsuite (MaterialSuite): The materialsuite whose content to
            create the technical metadata for
        2. working_dir (str): A path to a directory where the techmd creator
            can write files

        __KWArgs__

        * timeout (int): A timeout (in seconds) after which the technical
            metadata creation process will fail out, if it hasn't finished
        * data_transfer_obj (dict): A dictionary for passing techmd creator
            specific configuration values into the class from a wrapper.
        """
        log_init_attempt(self, log, locals())
        super().__init__(materialsuite, working_dir, timeout)
        self.fits_path = data_transfer_obj.get('fits_path', None)
        if self.fits_path is None:
            raise ValueError('No fits_path specified in the data ' +
                             'transfer object!')
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'source_materialsuite': str(self.source_materialsuite),
            'working_dir': str(self.working_dir),
            'timeout': self.timeout
        }
        return "<FITsCreator {}>".format(dumps(attr_dict, sort_keys=True))

    @log_aware(log)
    def process(self):
        """
        runs a local FITs installation against the MaterialSuite's content
        """
        if not isinstance(self.get_source_materialsuite().get_premis(),
                          LDRItem):
            raise ValueError("All material suites must have a PREMIS record " +
                             "in order to generate technical metadata.")
        log.debug("Building FITS-ing environment")
        premis_file_path = join(self.working_dir, str(uuid4()))
        LDRItemCopier(
            self.get_source_materialsuite().get_premis(),
            LDRPath(premis_file_path)
        ).copy()
        # hacky fix for not setting the originalName in presforms during the
        # staging tearup in response to some filename encodings not being
        # interoperable on different operating systems. (OSX/BSD/Windows/Linux)
        original_name = uuid4().hex

        content_file_path = dirname(
            join(
                self.working_dir,
                uuid4().hex,
                original_name
            )
        )
        content_file_containing_dir_path = dirname(content_file_path)
        makedirs(content_file_containing_dir_path, exist_ok=True)
        original_holder = LDRPath(content_file_path)
        LDRItemCopier(
            self.get_source_materialsuite().get_content(),
            original_holder
        ).copy()

        fits_file_path = join(self.working_dir, uuid4().hex)
        cmd = BashCommand([self.fits_path, '-i', content_file_path,
                           '-o', fits_file_path])

        if self.get_timeout() is not None:
            cmd.set_timeout(self.get_timeout())

        log.debug(
            "Running FITS on file. Timeout: {}".format(str(self.get_timeout()))
        )
        cmd.run_command()

        cmd_data = cmd.get_data()

        if isfile(fits_file_path):
            log.debug("FITS successfully created")
            self.get_source_materialsuite().add_technicalmetadata(
                LDRPath(fits_file_path)
            )
            self.handle_premis(cmd_data, self.get_source_materialsuite(),
                               "FITs", True)
        else:
            log.warn("FITS creation failed on {}".format(
                self.get_source_materialsuite().identifier)
            )
            self.handle_premis(cmd_data, self.get_source_materialsuite(),
                               "FITs", False)

        log.debug("Cleaning up temporary file instantiation")
        original_holder.delete(final=True)
