from .segmentstructure import SegmentStructure
from .materialsuite import MaterialSuiteStructure
from .ldrpathregularfile import LDRPathRegularFile
from .ldrpathregulardirectory import LDRPathRegularDirectory
from ..absolutefilepathtree import AbsoluteFilePathTree

class SegmentPackager(object):

    def __init__(self, a_directory, prefix, number=0):
        self.segment_input = AbsoluteFilePathTree(a_directory)
        self.label_descripter = prefix
        self.label_qualifier = number

    def create_segment(self):
        just_files = self.segment_input.get_files()
        all_nodes = self.segment_input.get_nodes()
        just_directories = [x.identifier for x in all_nodes
                                if x.identifier not in just_files]
        segment_id = self.label_descripter+str(self.label_qualifier)
        newsegment = SegmentStructure(self.label_descripter, segment_id)
        for n_thing in just_directories:
            a_file = LDRPathRegularDirectory(n_thing)
            msuite = MaterialSuiteStructure(a_file.item_name)
            msuite.original.append(a_file)
            newsegment.materialsuite.append(msuite)
        for n_thing in just_files:
            a_file = LDRPathRegularFile(n_thing)
            msuite = MaterialSuiteStructure(a_file.item_name)
            msuite.original.append(a_file)
            newsegment.materialsuite.append(msuite)
        return newsegment
