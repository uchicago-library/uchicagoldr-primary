from tempfile import TemporaryDirectory
from uuid import uuid1
from os import makedirs
from os.path import join, dirname
from mimetypes import guess_type

from pypremis.lib import PremisRecord
from pypremis.nodes import *
try:
    from magic import from_file
except:
    pass

from .ldrpath import LDRPath
from .materialsuite import MaterialSuite
from .ldritemoperations import copy
from .abc.ldritem import LDRItem


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class GenericPresformCreator(object):
    """
    Ingests a stage structure and produces presforms of files therein
    """
    def __init__(self, stage):
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
        self.converters = []

    def process(self, skip_existing=False, presform_presforms=False):
        for segment in self.stage.segment_list:
            for materialsuite in segment.materialsuite_list:
                if not isinstance(materialsuite.get_premis(), LDRItem):
                    raise ValueError("All material suites must have a PREMIS " +
                                     "record in order to generate presforms.")
                if skip_existing:
                    if isinstance(materialsuite.get_presform(0), MaterialSuite):
                        continue
                presforms, premis = self.instantiate_and_make_presforms(
                    materialsuite
                )
                if presforms:
                    materialsuite.set_presforms_list(presforms)
                if premis:
                    materialsuite.set_premis(premis)
                if presform_presforms:
                    if materialsuite.presform_list is not None:
                        for presform_ms in materialsuite.presform_list:
                            pres_presforms, pres_premis = \
                                self.instantiate_and_make_presforms(presform_ms)
                            if pres_presforms:
                                presform_ms.set_presform_list(pres_presforms)
                            if pres_premis:
                                presform_ms.set_premis(pres_premis)

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
        copy(ms.premis, premis_item, True)

        premis_rec = PremisRecord(frompath=premis_path)

        rec_obj = premis_rec.get_object_list()[0]
        rec_orig_name = rec_obj.get_originalName()

        conversion_dir_path = join(self.working_dir_path, str(uuid1()))
        recv_file = join(conversion_dir_path, rec_orig_name)
        recv_item = LDRPath(recv_file)
        makedirs(dirname(recv_file), exist_ok=True)
        copy(ms.content, recv_item, clobber=True)

        mime_from_ext = guess_type(recv_file)[0]
        try:
            mime_from_magic_no = from_file(recv_file)
        except:
            mime_from_magic_no = None

        presform_mss = []
        updated_premis = None

        for converter in self.converters:
            if mime_from_ext or mime_from_magic_no in converter.claimed_mimes:
                c = converter(recv_file, premis_path)
                presform_materialsuites, updated_premis_fp = c.convert()
                presform_mss = presform_mss + presform_materialsuites
                premis_path = updated_premis_fp
                updated_premis = LDRPath(premis_path)
        return (presform_mss, updated_premis)

