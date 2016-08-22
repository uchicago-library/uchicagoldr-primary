from tempfile import TemporaryDirectory
from json import dumps

from ..ldritems.abc.ldritem import LDRItem
from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from uchicagoldrtoolsuite.core.lib.exceptionhandler import ExceptionHandler


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)
eh = ExceptionHandler()


class GenericTechnicalMetadataCreator(object):
    """
    Ingests a stage structure and produces a FITS xml record for every
    file in it.
    """
    def __init__(self, stage, techmd_creators):
        """
        spawn a technical metadata creator that should work regardless of
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
        self.techmd_creators = techmd_creators
        log.debug("GenericTechnicalMetadataCreator spawned: {}".format(str(self)))

    def __repr__(self):
        attr_dict = {
            'stage': str(self.stage),
            'working_dir_path': self.working_dir_path,
            'techmd_creators': [str(x) for x in self.techmd_creators]
        }
        return "<GenericTechnicalMetadataCreator {}>".format(dumps(attr_dict, sort_keys=True))

    def process(self, skip_existing=False):
        log.debug("Beginning TECHMD Processing")
        s_num = 0
        for segment in self.stage.segment_list:
            s_num += 1
            ms_num = 0
            for materialsuite in segment.materialsuite_list:
                ms_num += 1
                log.debug("Processing section {}/{}, MaterialSuite {}/{}".format(
                    str(s_num),
                    str(len(self.stage.segment_list)),
                    str(ms_num),
                    str(len(segment.materialsuite_list)))
                )
                try:
                    if not isinstance(materialsuite.get_premis(), LDRItem):
                        raise ValueError("All material suites must have a PREMIS " +
                                        "record in order to generated technical " +
                                        "metadata records.")
                except Exception as e:
                    eh.handle(e)
                    continue
                if skip_existing:
                    if materialsuite.get_technicalmetadata_list():
                        if isinstance(materialsuite.get_technicalmetadata(0),
                                    LDRItem):
                            log.debug("Detected TECHMD: Skipping")
                            continue
                try:
                    log.debug("No TECHMD detected: Creating")
                    for techmd_creator in self.techmd_creators:
                        c = techmd_creator(materialsuite, self.working_dir_path)
                        c.process()
                    if materialsuite.presform_list is not None:
                        for presform_ms in materialsuite.presform_list:
                            if not isinstance(presform_ms.get_premis(), LDRItem):
                                raise ValueError("All material suites must have a PREMIS " +
                                                "record in order to generated technical " +
                                                "metadata records.")
                            c = techmd_creator(presform_ms, self.working_dir_path)
                            c.process()
                except Exception as e:
                    eh.handle(e)
