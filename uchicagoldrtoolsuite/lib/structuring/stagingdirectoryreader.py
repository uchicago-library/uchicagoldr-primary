'''
Created on Apr 13, 2016

@author: tdanstrom
'''

from .abc.stagingserializationreader import StagingSerializatinReader
from ..structuring.stagingstructure import StagingStructure
from ..absolutefilepathtree import AbsoluteFilePathTree
from .ldrpath import LDRPath

class StagingDirectoryReader(StagingSerializatinReader):
    def __init__(self, source_root, destination_root, a_directory):
        self.structure = StagingStructure
        self.structureType = "staging"

    def gather_resources(self, a_directory):
        tree = AbsoluteFilePathTree(a_directory)
        for n_thing in tree.get_nodes():
            LDRPath(n_thing.identifier)