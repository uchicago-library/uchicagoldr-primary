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
        self.structure = StagingStructure
        self.structureType = "staging"
        self.resources = []

    def gather_resources(self, a_directory):
        tree = AbsoluteFilePathTree(a_directory)
        for n_thing in tree:
            if n_thing.is_leaf():
                n_item = LDRPathRegularFile(n_thing)
            elif not n_thing.is_leaf():
                n_item = LDRPathRegularDirectory(n_thing)
            self.resources.append(n_item)

    