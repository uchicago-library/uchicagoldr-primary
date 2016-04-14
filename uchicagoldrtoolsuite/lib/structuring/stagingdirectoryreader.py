'''
Created on Apr 13, 2016

@author: tdanstrom
'''
from os.path import exists
from .abc.stagingserializationreader import StagingSerializatinReader
from ..structuring.stagingstructure import StagingStructure
from ..absolutefilepathtree import AbsoluteFilePathTree
from .ldrpathregularfile import LDRPathRegularFile
from .ldrpathregulardirectory import LDRPathRegularDirectory
from .segmentstructure import SegmentStructure

class StagingDirectoryReader(StagingSerializatinReader):
    def __init__(self, source_root, destination_root, a_directory, stage_id,
prefix, segment_number):
        super().__init__()
        self.structureType = "staging"
        self.stage_id = stage_id
        self.resources = []
        self.source_root = source_root
        self.destination_root = destination_root
        self.stage_directory = a_directory
        self.prefix = prefix
        self.segment_number = segment_number
        self.structure = self.read()

    def read(self):
        if exists(self.stage_directory):
            tree = AbsoluteFilePathTree(self.stage_directory)
            segment = SegmentStructure(self.prefix, self.segment_number)
            just_files = tree.get_fies()
            all_nodes = tree.get_nodes()
            just_directories = [x for x in all_nodes if not in just_files]
            for n_thing in just_directories:
                a_directory = LDRPathRegularDirectory(n_thing)
                prin(a_directory)
            for n_thing in just_files:
                a_file = LDRPathRegularFile(n_thing)
                print(a_file)
        else:
            return StagingStructure(self.stage_id)
        return "testing"

#     def gather_resources(self, a_directory):
#         tree = AbsoluteFilePathTree(a_directory)
#         for n_thing in tree:
#             if n_thing.is_leaf():
#                 n_item = LDRPathRegularFile(n_thing)
#             elif not n_thing.is_leaf():
#                 n_item = LDRPathRegularDirectory(n_thing)
#             self.resources.append(n_item)
# 
#     
