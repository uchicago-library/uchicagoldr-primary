from tempfile import TemporaryDirectory
from uuid import uuid1
from os import makedirs
from os.path import join
from json import dumps

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
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

        stage (Stage): the Stage to operate on
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

    def process(self, skip_existing=False, presform_presforms=False):
        for segment in self.stage.segment_list:
            for materialsuite in segment.materialsuite_list:
                if not isinstance(materialsuite.get_premis(), LDRItem):
                    raise ValueError("All material suites must have a PREMIS " +
                                     "record in order to generate presforms.")
                if skip_existing:
                    try:
                        if isinstance(materialsuite.get_presform(0),
                                      MaterialSuite):
                            continue
                    except:
                        pass
                self.instantiate_and_make_presforms(materialsuite)
                if presform_presforms:
                    if materialsuite.presform_list is not None:
                        for presform_ms in materialsuite.presform_list:
                            self.instantiate_and_make_presforms(presform_ms)

    def instantiate_and_make_presforms(self, ms):
        """
        write the file to disk an examine it, update its PREMIS

        __Args__

        1. ms (MaterialSuite): The MaterialSuite of the item in question

        __Returns__

        * (tuple): The first entry is a list of presform LDRItems
            The second is the updated PREMIS record.
        """
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
        for converter in self.converters:
            for x in mimes:
                if x in converter._claimed_mimes:
                    c_working_dir = join(self.working_dir_path, str(uuid1()))
                    makedirs(c_working_dir, exist_ok=True)
                    c = converter(ms, c_working_dir)
                    c.convert()
