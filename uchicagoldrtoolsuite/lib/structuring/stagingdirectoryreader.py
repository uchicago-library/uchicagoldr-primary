'''
Created on Apr 13, 2016

@author: tdanstrom
'''
import re
from os.path import exists, join, split as dirsplit
from .abc.stagingserializationreader import StagingSerializatinReader
from ..structuring.stagingstructure import StagingStructure
from ..absolutefilepathtree import AbsoluteFilePathTree
from .ldrpathregularfile import LDRPathRegularFile
from .ldrpathregulardirectory import LDRPathRegularDirectory
from .materialsuite import MaterialSuiteStructure
from .segmentstructure import SegmentStructure

class StagingDirectoryReader(StagingSerializatinReader):
    def __init__(self, stage_id, src_root, dest_root, stageable_directory,
                 prefix, prefixnum):
        super().__init__()
        self.structureType = "staging"
        self.destination_root = dest_root
        self.source_root = src_root
        self.directory_to_stage = stageable_directory
        self.stage_id = stage_id
        self.prefix = prefix
        self.segment_number = prefixnum
        self.stage_directory = join(self.destination_root, self.stage_id)
        self.structure = self.read()

    def read(self):
        if exists(self.stage_directory):
            tree = AbsoluteFilePathTree(self.stage_directory)
            segment = SegmentStructure(self.prefix, str(self.segment_number))
            just_files = tree.get_files()
            all_nodes = tree.get_nodes()
            just_directories = [x.identifier for x in all_nodes
                                if x.identifier not in just_files]
            data_node_identifier = join(self.stage_directory, 'data')
            data_node_depth = tree.find_depth_of_a_path(data_node_identifier)
            data_node = tree.find_tag_at_depth('data', data_node_depth)[0]
            data_node_subdirs = data_node.fpointer
            stagingstructure = StagingStructure(self.stage_id)
            for n in data_node_subdirs:
                a_past_segment_node_depth = tree.find_depth_of_a_path(n)
                if a_past_segment_node_depth > 0:
                    label = dirsplit(n)[1]
                    valid_pattern = re.compile('(\w{1,})(\d{1,})')
                    label_matching = valid_pattern.match(label)           
                    if label_matching:
                        prefix, number = label_matching.group(1), label_matching.group(2)
                        a_new_segment = SegmentStructure(prefix, number)
                        stagingstructure.segment.append(a_new_segment)

            for n_thing in just_directories:
                segment_id = join(self.stage_directory, 'data/')
                if segment_id in n_thing:
                    split_from_segment_id = n_thing.split(segment_id)
                    if len(split_from_segment_id) == 2:
                        file_run = split_from_segment_id[1].split('/')[0]
                        matching_segment = [x for x in stagingstructure.segment if x.identifier == file_run]
                        if len(matching_segment) == 1:
                            a_file = LDRPathRegularDirectory(n_thing)
                            msuite = MaterialSuiteStructure(a_file.item_name)
                            msuite.original.append(a_file)
                            matching_segment[0].materialsuite.append(msuite)
                        else:
                            stderr.write("There are more than one segments in the staging structure with id {}\n".\
                                         format(file_run))
                    else:
                        stderr.write("the path for {} is wrong.\n".format(n_thing))

            for n_thing in just_files:
                segment_id = join(self.stage_directory, 'data/')
                if segment_id in n_thing:
                    split_from_segment_id = n_thing.split(segment_id)
                    if len(split_from_segment_id) == 2:
                        file_run = split_from_segment_id[1].split('/')[0]
                        matching_segment = [x for x in stagingstructure.segment if x.identifier == file_run]
                        if len(matching_segment) == 1:
                            a_file = LDRPathRegularFile(n_thing)
                            msuite = MaterialSuiteStructure(a_file.item_name)
                            msuite.original.append(a_file)
                            matching_segment[0].materialsuite.append(msuite)
                        else:
                            stderr.write("There are more than one segments in the staging structure with id {}\n".\
                                         format(file_run))
                    else:
                        stderr.write("the path for {} is wrong.\n".format(n_thing))

        else:
            stagingstructure = StagingStructure(self.stage_id)

        return stagingstructure
    
    
    def add_to_structure(self):
        tree = AbsoluteFilePathTree(self.directory_to_stage)
        just_files = tree.get_files()
        all_nodes = tree.get_nodes()
        just_directories = [x.identifier for x in all_nodes
                                if x.identifier not in just_files]
        last_segments = self.structure.segment
        pattern_match = re.compile('(\w{1,})(\d{1,})')
        potential_past_relevant_segments = []
        for n_segment in last_segments:
            pattern_match_group = pattern_match.match(n_segment.identifier)
            prefix, number = pattern_match_group.group(1), pattern_match_group.group(2)
            if prefix == self.prefix:
                potential_past_relevant_segments.append(n_segment)
        potential_past_relevant_segments.sort(key=lambda x: x.identifier)
        if len(potential_past_relevant_segments) > 0:
            last_segment = potential_past_relevant_segments[-1]
            current_segment_num = str(int(pattern_match.match(last_segment.identifier).\
                                          group(2))+1)
        else:
            current_segment_id = '1'
        newsegment = SegmentStructure(self.prefix, current_segment_num)

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
        self.structure.segment.append(newsegment)
