'''
Created on Apr 13, 2016

@author: tdanstrom
'''

from .abc.stagingserializationreader import StagingSerializatinReader
from ..structuring.stagingstructure import StagingStructure
from ..absolutefilepathtree import AbsoluteFilePathTree
from .ldrpathregularfile import LDRPathRegularFile
from .ldrpathregulardirectory import LDRPathRegularDirectory

class StagingDirectoryReader(StagingSerializatinReader):
    def __init__(self, source_root, destination_root, a_directory):
        super().__init__()
        self.structure = self.read()
        self.structureType = "staging"
        self.resources = []
        self.source_root = source_root
        self.destination_root = destination_root
        self.stage_directory = a_directory
        
    def read(self):
        tree = AbsoluteFilePathTree(self.stage_directory)
        for n_thing in tree.get_nodes():
            print(n_thing)
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