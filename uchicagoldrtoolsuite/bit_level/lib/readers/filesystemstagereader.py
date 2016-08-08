import re
from os.path import exists, join, isfile, split as dirsplit

from .abc.stageserializationreader import StageSerializationReader
from ..fstools.absolutefilepathtree import AbsoluteFilePathTree
from .filesystemsegmentpackager import FileSystemSegmentPackager
from ..ldritems.ldrpath import LDRPath
from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"

log = spawn_logger(__name__)


class FileSystemStageReader(StageSerializationReader):
    """
    Repackages files written to disk as a Staging Structure
    """
    def __init__(self, staging_directory):
        """
        spawn a reader

        __Args__

        1. staging_directory (str): The path to the Stage on disk
        """
        log.debug(
            "FileSystemStageReader for {} spawned".format(
                staging_directory
            )
        )
        super().__init__()
        self.set_implementation('file system')
        log.debug(
            "Splitting {} to get env and id".format(
                staging_directory
            )
        )
        self.stage_id = staging_directory.split('/')[-1]
        self.get_struct().set_identifier(staging_directory.split('/')[-1])
        self.stage_env_path = "/".join(staging_directory.split('/')[0:-1])
        self.structureType = "staging"
        self.serialized_location = staging_directory
        log.debug("Stage Env: {}".format(self.stage_env_path))
        log.debug("Stage ID: {}".format(self.stage_id))

    def read(self):
        log.debug(
            "Beginning Read of {}".format(
                join(self.stage_env_path, self.stage_id)
            )
        )

        log.debug(
            "Determining existence of {}".format(
                join(self.stage_env_path, self.stage_id)
            )
        )

        if exists(self.serialized_location):
            log.debug(
                "{} exists".format(
                    self.serialized_location
                )
            )

            log.debug(
                "Creating AbsoluteFilePathTree for {}".format(
                    self.serialized_location
                )
            )
            tree = AbsoluteFilePathTree(
                self.serialized_location, leaf_dirs=True
            )
            log.debug(
                "AbsoluteFilePathTree for {} created".format(
                    self.serialized_location
                )
            )
            log.debug(
                "Examining Tree constructed from {}".format(
                    self.serialized_location
                )
            )
            data_node_identifier = join(self.serialized_location, 'data')
            data_node_depth = tree.find_depth_of_a_path(data_node_identifier)
            data_node = tree.find_tag_at_depth('data', data_node_depth)[0]
            data_node_subdirs = data_node.fpointer
            log.debug(
                "Beginning segment packaging from {}".format(
                    self.serialized_location
                )
            )
            seg_num = 0
            for n in data_node_subdirs:
                seg_num += 1
                log.debug(
                    "Reading Segment {}/{} from {}".format(
                        str(seg_num),
                        str(len(data_node_subdirs)),
                        self.stage_id
                    )
                )
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
                            ).package()
                        )
                    else:
                        log.critical(
                            "the path for {} is wrong.".format(
                                label
                            )
                        )

            log.debug(
                "Packaging non-segmented material from {}".format(
                    self.serialized_location
                )
            )
            log.debug(
                "Processing admin node in {}".format(
                    self.serialized_location
                )
            )
            admin_node_identifier = join(self.serialized_location, 'admin')
            admin_node_depth = tree.find_depth_of_a_path(admin_node_identifier)
            legalnotes_node = tree.find_tag_at_depth(
                'legalnotes', admin_node_depth+1)[0]
            adminnotes_node = tree.find_tag_at_depth(
                'adminnotes', admin_node_depth+1)[0]
            accessionrecords_node = tree.find_tag_at_depth(
                'accessionrecords', admin_node_depth+1)[0]

            adminnotes_files = adminnotes_node.fpointer
            legalnotes_files = legalnotes_node.fpointer
            accessionrecords_files = accessionrecords_node.fpointer

            log.debug(
                "Reading adminnotes in {}".format(
                    self.serialized_location
                )
            )
            for x in adminnotes_files:
                if not isfile(x):
                    raise OSError("The contents of the adminnote dir must " +
                                  "be just files")
                i = LDRPath(x, root=adminnotes_node.identifier)
                self.get_struct().add_adminnote(i)

            log.debug(
                "Reading legalnotes in {}".format(
                    self.serialized_location
                )
            )
            for x in legalnotes_files:
                if not isfile(x):
                    raise OSError("The contents of the legalnote dir must " +
                                  "be just files")
                i = LDRPath(x, root=legalnotes_node.identifier)
                self.get_struct().add_legalnote(i)

            log.debug(
                "Reading accessionrecords in {}".format(
                    self.serialized_location
                )
            )
            for x in accessionrecords_files:
                if not isfile(x):
                    raise OSError("The contents of the accessionrecord dir " +
                                  "must be just files")
                i = LDRPath(x, root=accessionrecords_node.identifier)
                self.get_struct().add_accessionrecord(i)

            log.debug(
                "Segment packaging from {} complete".format(
                    self.serialized_location
                )
            )
        else:
            log.debug(
                "{} does not exist".format(
                    self.serialized_location
                )
            )

        log.debug(
            "Read of {} complete".format(
                self.serialized_location
            )
        )
        return self.get_struct()
