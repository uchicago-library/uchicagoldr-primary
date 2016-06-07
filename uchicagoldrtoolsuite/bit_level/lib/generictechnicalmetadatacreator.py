from tempfile import TemporaryDirectory


from .abc.ldritem import LDRItem


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


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

    def process(self, skip_existing=False):
        for segment in self.stage.segment_list:
            for materialsuite in segment.materialsuite_list:
                if not isinstance(materialsuite.get_premis(), LDRItem):
                    raise ValueError("All material suites must have a PREMIS " +
                                     "record in order to generated technical " +
                                     "metadata records.")
                if skip_existing:
                    if isinstance(materialsuite.get_technicalmetadata(0),
                                  LDRItem):
                        continue
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
