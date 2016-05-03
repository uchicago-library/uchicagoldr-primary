import re
from sys import stderr
from os.path import exists, join, split as dirsplit
from ..lib.stagingserializationreader import StagingSerializationReader
from ..lib.stagingstructure import StagingStructure
from ..lib.absolutefilepathtree import AbsoluteFilePathTree
from .ldrpath import LDRPath
from ..lib.materialsuitestructure import MaterialSuiteStructure
from ..lib.segmentstructure import SegmentStructure
'''
Created on Apr 13, 2016
@author: tdanstrom
'''


class FileSystemStagingStructureReader(StagingSerializationReader):
    def __init__(self, staging_directory):
        self.stage_id = staging_directory.split('/')[-1]
        self.structureType = "staging"
        self.serialized_location = staging_directory

    def read(self):
        if exists(self.serialized_location):
            tree = AbsoluteFilePathTree(self.serialized_location)
            just_files = tree.get_files()
            data_node_identifier = join(self.serialized_location, 'data')
            data_node_depth = tree.find_depth_of_a_path(data_node_identifier)
            data_node = tree.find_tag_at_depth('data', data_node_depth)[0]
            data_node_subdirs = data_node.fpointer
            stagingstructure = StagingStructure(self.
                                                serialized_location.
                                                split('/')[-1])
            for n in data_node_subdirs:
                a_past_segment_node_depth = tree.find_depth_of_a_path(n)
                if a_past_segment_node_depth > 0:
                    label = dirsplit(n)[1]
                    valid_pattern = re.compile('(\w{1,})-(\d{1,})')
                    label_matching = valid_pattern.match(label)
                    if label_matching:
                        prefix, number = label_matching.group(1), \
                                         label_matching.group(2)
                        a_new_segment = SegmentStructure(prefix, int(number))
                        stagingstructure.segment.append(a_new_segment)
            for n_thing in just_files:
                segment_id = join(self.serialized_location, 'data/')
                if segment_id in n_thing:
                    split_from_segment_id = n_thing.split(segment_id)
                    if len(split_from_segment_id) == 2:
                        file_run = split_from_segment_id[1].split('/')[0]
                        matching_segment = [x for x in stagingstructure.segment
                                            if x.identifier == file_run]
                        if len(matching_segment) == 1:
                            a_file = LDRPath(n_thing)
                            msuite = MaterialSuiteStructure(a_file.item_name)
                            msuite.original.append(a_file)
                            matching_segment[0].materialsuite.append(msuite)
                        else:
                            stderr.write("There are more than one segments in" +
                                         " the staging structure with id {}\n".
                                         format(file_run))
                    else:
                        stderr.write("the path for {} is wrong.\n".format(
                            n_thing))

        else:
            stagingstructure = StagingStructure(self.stage_id)
        return stagingstructure

    def set_structure(self, aStructure):
        self.structure = aStructure

    def get_stage_id(self):
        return self._stage_id

    def set_stage_id(self, value):
        self._stage_id = value

    stage_id = property(get_stage_id, set_stage_id)
