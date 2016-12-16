from tempfile import TemporaryDirectory
from json import dumps
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from ..ldritems.abc.ldritem import LDRItem


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


# This class doesn't have a function in it that lends itself to easily splitting
# into a @classmethod (see #98). Before any major work occurs in this class for
# whatever reason that should probably be remedied.

log = getLogger(__name__)


class GenericTechnicalMetadataCreator(object):
    """
    Ingests a stage structure and produces a FITS xml record for every
    file in it.
    """
    @log_aware(log)
    def __init__(self, stage, techmd_creators):
        """
        spawn a technical metadata creator that should work regardless of
        what kind of LDRItems are being used

        __Args__

        stage (Stage): the Stage to operate on
        """
        log_init_attempt(self, log, locals())
        self.stage = stage
        # This instance var should hold the dir open until the instance is
        # deleted from whatever script spawned it. Aka move this stuff
        # somewhere before your instance gets garbage collected.
        self.working_dir = TemporaryDirectory()
        self.working_dir_path = self.working_dir.name
        self.techmd_creators = techmd_creators
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'stage': str(self.stage),
            'working_dir_path': self.working_dir_path,
            'techmd_creators': [str(x) for x in self.techmd_creators]
        }
        return "<GenericTechnicalMetadataCreator {}>".format(
            dumps(attr_dict, sort_keys=True)
        )

    @log_aware(log)
    def process(self, skip_existing=False, data_transfer_obj={}):
        """
        create technical metadata for the provided stage

        __KWArgs__

        * skip_existing (bool): if True and the MaterialSuite has >0 technical
            metadata records then skip it
        * data_transfer_obj (dict): A dictionary for techmd creator specific
            configuration options
        """
        log.debug("Beginning TECHMD Processing")
        ms_num = 0
        for materialsuite in self.stage.materialsuite_list:
            ms_num += 1
            log.debug(
                "Processing MaterialSuite {}/{}".format(
                    str(ms_num),
                    str(len(self.stage.materialsuite_list))
                )
            )
            if not isinstance(materialsuite.get_premis(), LDRItem):
                raise ValueError("All material suites must have a PREMIS " +
                                 "record in order to generated technical " +
                                 "metadata records.")
                continue
            if not materialsuite.content:
                continue
            if skip_existing:
                if materialsuite.get_technicalmetadata_list():
                    if isinstance(materialsuite.get_technicalmetadata(0),
                                  LDRItem):
                        log.debug("Detected TECHMD: Skipping")
                        continue
            log.debug("No TECHMD detected: Creating")
            for techmd_creator in self.techmd_creators:
                c = techmd_creator(materialsuite, self.working_dir_path,
                                   data_transfer_obj=data_transfer_obj)
                c.process()
