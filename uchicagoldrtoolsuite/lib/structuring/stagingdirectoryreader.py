'''
Created on Apr 13, 2016

@author: tdanstrom
'''

from .abc.stagingserializationreader import StagingSerializatinReader
from lib.structuring.stagingstructure import StagingStructure

class StagingDirectoryReader(StagingSerializatinReader):
    def __init__(self, source_root, destination_root, a_directory):
        self.source_root = source_root
        self.destination_root = destination_root
        self.structure = StagingStructure
        self.structureType = "staging"
        
        
    def gather_resources(self, ):
        