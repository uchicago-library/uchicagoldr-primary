from tempfile import TemporaryDirectory
from uuid import uuid1
from os import makedirs
from os.path import join
from json import dumps

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from uchicagoldrtoolsuite.core.lib.convenience import \
    is_presform_materialsuite, TemporaryFilePath, ldritem_to_premisrecord
from ..ldritems.ldrpath import LDRPath
from ..structures.materialsuite import MaterialSuite
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.abc.ldritem import LDRItem


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class GenericPresformCreator(object):
    """
    Ingests a stage structure and produces presforms of files therein
    """
    def __init__(self, stage, converters):
        """
        spawn a presform creator that should work regardless of
        what kind of LDRItems are being used

        __Args__

        1. stage (Stage): the Stage to operate on
        2. converters ([Converter]): an array of the converters to use
        """
        self.stage = stage
        # This instance var should hold the dir open until the instance is
        # deleted from whatever script spawned it. Aka move this stuff
        # somewhere before your instance gets garbage collected.
        self.working_dir = TemporaryDirectory()
        self.working_dir_path = self.working_dir.name
        self.converters = converters
        log.debug("GenericPresformCreator spawned: {}".format(str(self)))

    def __repr__(self):
        attr_dict = {
            'stage': str(self.stage),
            'working_dir_path': self.working_dir_path,
            'converters': [str(x) for x in self.converters]
        }
        return "<GenericPresformCreator {}>".format(dumps(attr_dict, sort_keys=True))

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
        for segment in self.stage.segment_list:
            stuff_to_add_to_segment = []
            for materialsuite in segment.materialsuite_list:
                if not isinstance(materialsuite.get_premis(), LDRItem):
                    raise ValueError("All material suites must have a PREMIS " +
                                     "record in order to generate presforms.")
                if is_presform_materialsuite(materialsuite) and not \
                        presform_presforms:
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
                        continue
                for x in self.instantiate_and_make_presforms(materialsuite,
                                                             data_transfer_obj=data_transfer_obj):
                    stuff_to_add_to_segment.append(x)
            for x in stuff_to_add_to_segment:
                segment.add_materialsuite(x)

    def instantiate_and_make_presforms(self, ms, data_transfer_obj={}):
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
            return []
        premis_path = join(self.working_dir_path, str(uuid1()))
        premis_item = LDRPath(premis_path)
        c = LDRItemCopier(ms.premis, premis_item, clobber=True)
        c.copy()

        premis_rec = PremisRecord(frompath=premis_path)

        rec_obj = premis_rec.get_object_list()[0]

        mimes = []
        for rec_obj_chars in rec_obj.get_objectCharacteristics():
            for rec_format in rec_obj_chars.get_format():
                fmt_dsg = rec_format.get_formatDesignation()
                if fmt_dsg:
                    mimes.append(fmt_dsg.get_formatName())
        converters_to_run = []
        for converter in self.converters:
            for x in mimes:
                if converter.handles_mime(x):
                    converters_to_run.append(converter)
                    break

        presforms = []
        for converter in set(converters_to_run):
            c_working_dir = join(self.working_dir_path, str(uuid1()))
            makedirs(c_working_dir, exist_ok=True)
            c = converter(ms, c_working_dir,
                            data_transfer_obj=data_transfer_obj)
            presform = c.convert()
            if presform is not None:
                presforms.append(presform)
        return presforms
