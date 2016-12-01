from tempfile import TemporaryDirectory
from uuid import uuid1
from os import makedirs
from os.path import join
from json import dumps
from logging import getLogger

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import \
    is_presform_materialsuite, ldritem_to_premisrecord
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from ..ldritems.ldrpath import LDRPath
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.abc.ldritem import LDRItem


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class GenericPresformCreator(object):
    """
    Ingests a stage structure and produces presforms of files therein
    """
    @log_aware(log)
    def __init__(self, stage, converters):
        """
        spawn a presform creator that should work regardless of
        what kind of LDRItems are being used

        __Args__

        1. stage (Stage): the Stage to operate on
        2. converters ([Converter]): an array of the converters to use
        """
        log_init_attempt(self, log, locals())
        self.stage = stage
        # This instance var should hold the dir open until the instance is
        # deleted from whatever script spawned it. Aka move this stuff
        # somewhere before your instance gets garbage collected.
        self.working_dir = TemporaryDirectory()
        self.working_dir_path = self.working_dir.name
        self.converters = converters
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'stage': str(self.stage),
            'working_dir_path': self.working_dir_path,
            'converters': [str(x) for x in self.converters]
        }
        return "<GenericPresformCreator {}>".format(dumps(attr_dict, sort_keys=True))

    @log_aware(log)
    def process(self, skip_existing=False, presform_presforms=False,
                data_transfer_obj={}):
        """
        Iterate over all the MaterialSuites in the stage, creating presforms

        __KWArgs__

        * skip_existing (bool): If True and a presform already exists (as
            determined by the PREMIS record) skip the MaterialSuite
        * presform_presforms (bool): If True operate on MaterialSuites
            that contain presform data, otherwise skip them
        * data_trans_obj (dict): A dictionary containing converter specific
            configuration values
        """
        log.debug("Beginning stage level processing")
        seg_len = len(self.stage.segment_list)
        seg_num = 0
        for segment in self.stage.segment_list:
            seg_num = seg_num + 1
            log.debug("Processing Segment {}/{}".format(seg_num, seg_len))
            stuff_to_add_to_segment = []
            ms_len = len(segment.materialsuite_list)
            ms_num = 0
            for materialsuite in segment.materialsuite_list:
                ms_num = ms_num + 1
                log.debug(
                    "Processing MaterialSuite {}/{} ".format(ms_num, ms_len) +
                    "in Segment {}/{}".format(seg_num, seg_len)
                )
                if not isinstance(materialsuite.get_premis(), LDRItem):
                    raise ValueError("All material suites must have a PREMIS " +
                                     "record in order to generate presforms.")
                if is_presform_materialsuite(materialsuite) and not \
                        presform_presforms:
                    log.debug("Materialsuite contains a presform and " +
                              "presform_presforms == False. Skipping.")
                    continue
                if skip_existing:
                    has_presforms = False
                    premis = ldritem_to_premisrecord(materialsuite.premis)
                    try:
                        for relation in premis.get_object_list()[0].get_relationship():
                            if relation.get_relationshipType() == 'derivation' \
                                    and relation.get_relationshipSubType() == 'is Source of':
                                has_presforms = True
                                break
                    except KeyError:
                        pass
                    if has_presforms:
                        log.debug("MaterialSuite already has at least one " +
                                  "presform and skip_existing == True. " +
                                  "Skipping.")
                        continue
                for x in self.instantiate_and_make_presforms(materialsuite,
                                                             self.working_dir_path,
                                                             self.converters,
                                                             data_transfer_obj=data_transfer_obj):
                    stuff_to_add_to_segment.append(x)
            for x in stuff_to_add_to_segment:
                segment.add_materialsuite(x)

    @staticmethod
    @log_aware(log)
    def instantiate_and_make_presforms(ms, working_dir_path, converters,
                                       data_transfer_obj={}):
        """
        write the file to disk an examine it, update its PREMIS

        __Args__

        1. ms (MaterialSuite): The MaterialSuite of the item in question

        __Returns__

        * presforms (list[MaterialSuite]): a list of materialsuites,
            which represent the preservation stable copies of the original file
            as well as their associated PREMIS
        """
        if not ms.content:
            log.debug("MaterialSuite has no content, no presforms created.")
            return []
        log.debug("Instantiating original PREMIS")
        premis_path = join(working_dir_path, str(uuid1()))
        premis_item = LDRPath(premis_path)
        c = LDRItemCopier(ms.premis, premis_item, clobber=True)
        c.copy()

        log.debug("Reading PREMIS...")
        premis_rec = PremisRecord(frompath=premis_path)

        rec_obj = premis_rec.get_object_list()[0]

        log.debug("Looking for mime types in PREMIS...")
        mimes = []
        for rec_obj_chars in rec_obj.get_objectCharacteristics():
            for rec_format in rec_obj_chars.get_format():
                fmt_dsg = rec_format.get_formatDesignation()
                if fmt_dsg:
                    mimes.append(fmt_dsg.get_formatName())
        log.debug("Detected mime types: {}".format(str(mimes)))
        converters_to_run = []
        log.debug("Getting converters to run")
        for converter in converters:
            for x in mimes:
                if converter.handles_mime(x):
                    converters_to_run.append(converter)
                    break
        log.debug("Converters to be run: {}".format(str(converters_to_run)))

        presforms = []
        for converter in set(converters_to_run):
            log.debug("Attempting to run converter: {}".format(str(converter)))
            c_working_dir = join(working_dir_path, str(uuid1()))
            makedirs(c_working_dir, exist_ok=True)
            c = converter(ms, c_working_dir,
                          data_transfer_obj=data_transfer_obj)
            presform = c.convert()
            if presform is not None:
                presforms.append(presform)
                log.debug("Presform generated")
            else:
                log.debug("No presform generated")
        log.debug("All converters run")
        return presforms
