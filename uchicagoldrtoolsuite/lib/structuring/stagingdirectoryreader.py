'''
Created on Apr 13, 2016

@author: tdanstrom
'''
from os.path import exists, join, split as dirsplit
from .abc.stagingserializationreader import StagingSerializatinReader
from ..structuring.stagingstructure import StagingStructure
from ..absolutefilepathtree import AbsoluteFilePathTree
from .ldrpathregularfile import LDRPathRegularFile
from .ldrpathregulardirectory import LDRPathRegularDirectory
from .materialsuite import MaterialSuiteStructure
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
            just_files = tree.get_files()
            all_nodes = tree.get_nodes()
            just_directories = [x.identifier for x in all_nodes
                                if x.identifier not in just_files]
            data_node_identifier = join(self.stage_directory, 'data')
            data_node_depth = tree.find_depth_of_a_path(data_node_identifier)
            data_node = tree.find_tag_at_depth('data', data_node_depth)[0]
            data_node_subdirs = data_node.fpointer
            for n in data_node_subdirs:
                a_past_segment_node_depth = tree.find_depth_of_a_path(n)
                print(n)
                print(a_past_segment_node_depth)
                prefix_and_num = '/'+dirsplit(n)[1]
                print(tree.find_tag_at_depth('/data'+prefix_and_num, 6))
                # print(tree.find_tag_at_depth(join('/data/',
                #                                   dirsplit(n)[0].split('/')[-1]),
                #                              a_past_segment_node_depth))

            #depth_of_data_node = tree.find_depth_of_a_path(data_node_identifier)

            # if len(data_node_subdirs) == 1:
            #     data_node_subdirs = 
            # print(data_node_subdirs)
            # for n_thing in just_directories:

            #     a_directory = LDRPathRegularDirectory(n_thing)
            #     msuite = MaterialSuiteStructure(a_directory.item_name)
            #     msuite.original.append(a_directory)
            #     segment.materialsuite.append(msuite)
            # for n_thing in just_files:
            #     a_file = LDRPathRegularFile(n_thing)
            #     msuite = MaterialSuiteStructure(a_file.item_name)
            #     msuite.original.append(a_file)
            #     segment.materialsuite.append(msuite)
            # stagingstructure = StagingStructure(self.stage_id)
            # stagingstructure.segment.append(segment)
            stagingstructure = StagingStructure(self.stage_id)
        else:
            stagingstructure = StagingStructure(self.stage_id)

        return stagingstructure
