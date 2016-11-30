from os import makedirs
from os.path import join, dirname, isfile
from uuid import uuid1
from requests import post
from xml.etree.ElementTree import fromstring
from json import dumps
from logging import getLogger

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite import log_aware
from ..ldritems.ldrpath import LDRPath
from ..ldritems.abc.ldritem import LDRItem
from .abc.technicalmetadatacreator import TechnicalMetadataCreator
from ..ldritems.ldritemcopier import LDRItemCopier
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, log_init_success


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class APIFITsCreator(TechnicalMetadataCreator):
    @log_aware(log)
    def __init__(self, materialsuite, working_dir, timeout=None,
                 data_transfer_obj={}):
        """
        Creates a new instance of an APIFitsCreator.

        __Args__

        1. materialsuite (MaterialSuite): The MaterialSuite which
            contains the content to generate technical metadata for.
        2. working_dir (str): A location on disk where the FITsCreator
            can write files

        __KWArgs__

        * timeout (int): A timeout for the techmd creation process, after
            which the creator will fail out.
        * data_transfer_obj (dict): A dictionary for passing converter
            specific information into the class from a wrapper.
        """
        log_init_attempt(self, log, locals())
        super().__init__(materialsuite, working_dir, timeout)
        self.fits_api_url = data_transfer_obj.get('fits_api_url', None)
        if self.fits_api_url is None:
            raise ValueError('No fits_api_url specified in the data ' +
                             'transfer object!')
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'source_materialsuite': str(self.source_materialsuite),
            'working_dir': str(self.working_dir),
            'timeout': self.timeout,
            'api_url': self.fits_api_url
        }
        return "<APIFITsCreator {}>".format(dumps(attr_dict, sort_keys=True))

    @log_aware(log)
    def process(self):
        """
        Attempts to create the technical metadata for the MaterialSuite.

        Alters the MaterialSuite in place.
        """
        log.debug(
            "Attempting to create FITS for {}".format(
                self.get_source_materialsuite().get_content().item_name
            )
        )
        log.debug(
            "Building FITsCreator environment."
        )
        if not isinstance(self.get_source_materialsuite().get_premis(),
                          LDRItem):
            raise ValueError("All material suites must have a PREMIS record " +
                             "in order to generate technical metadata.")
        premis_file_path = join(self.working_dir, str(uuid1()))
        LDRItemCopier(
            self.get_source_materialsuite().get_premis(),
            LDRPath(premis_file_path)
        ).copy()
        premis_record = PremisRecord(frompath=premis_file_path)
        original_name = premis_record.get_object_list()[0].get_originalName()

        content_file_path = dirname(
            join(
                self.working_dir,
                str(uuid1()),
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

        fits_file_path = join(self.working_dir, str(uuid1()))
        if self.get_timeout() is not None:
            log.debug("The API FITS generator doesn't support timeouts.")

        log.debug("POSTing file to endpoint.")
        exc = None
        try:
            r = post(
                self.fits_api_url,
                files={'datafile': original_holder.open()}
            )

            if fromstring(r.text).tag == "error":
                raise ValueError(r.text)
            else:
                with open(fits_file_path, 'w') as f:
                    f.write(r.text)
            log.debug("FITS creation successful")
        except Exception as e:
            log.warn("FITS creation failed: {}".format(str(e)))
        log.debug("Updating PREMIS")
        if isfile(fits_file_path):
            self.get_source_materialsuite().add_technicalmetadata(
                LDRPath(fits_file_path)
            )
            self.handle_premis(
                "Successfully retrieved FITS from API",
                self.get_source_materialsuite(),
                "FITs", True
            )
        else:
            self.handle_premis(
                "Failed Retrieving FITS from API ({})".format(str(exc)),
                self.get_source_materialsuite(),
                "FITs", False
            )

        log.debug("Deleting temporary holder file")
        original_holder.delete(final=True)
