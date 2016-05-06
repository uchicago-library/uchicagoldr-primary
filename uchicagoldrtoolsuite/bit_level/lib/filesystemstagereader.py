import re
from sys import stderr
from os.path import exists, join, split as dirsplit

from .abc.stageserializationreader import StageSerializationReader
from .absolutefilepathtree import AbsoluteFilePathTree
from .filesystemsegmentpackager import FileSystemSegmentPackager


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class FileSystemStageReader(StageSerializationReader):
    """
    Repackages files written to disk as a Staging Structure
    """
    def __init__(self, staging_directory):
        super().__init__()
        self.set_implementation('file system')
        self.stage_id = staging_directory.split('/')[-1]
        self.get_struct().set_identifier(staging_directory.split('/')[-1])
        self.stage_env_path = staging_directory.split('/')[0:-1]
        self.structureType = "staging"
        self.serialized_location = staging_directory

    def read(self):
        if exists(self.serialized_location):
            tree = AbsoluteFilePathTree(self.serialized_location)
            data_node_identifier = join(self.serialized_location, 'data')
            data_node_depth = tree.find_depth_of_a_path(data_node_identifier)
            data_node = tree.find_tag_at_depth('data', data_node_depth)[0]
            data_node_subdirs = data_node.fpointer
            for n in data_node_subdirs:
                a_past_segment_node_depth = tree.find_depth_of_a_path(n)
                if a_past_segment_node_depth > 0:
                    label = dirsplit(n)[1]
                    valid_pattern = re.compile('(\w{1,})-(\d{1,})')
                    label_matching = valid_pattern.match(label)
                    if label_matching:
                        prefix, number = label_matching.group(1), \
                                         label_matching.group(2)
                        self.get_struct().add_segment(
                            FileSystemSegmentPackager(
                                self.stage_env_path,
                                self.stage_id,
                                prefix,
                                number
                            )
                        )
                    else:
                        stderr.write("the path for {} is wrong.\n".format(
                            n_thing))
            # Go on to handle adminnote, legalnote, acc rec
        return self.get_struct()
