
from os.path import join
import re
from itertools import chain
from os.path import relpath
from uchicagoldrtoolsuite.apps.internals.cliapp import CLIApp
from uchicagoldrtoolsuite.lib.structuring.stagingdirectoryreader import StagingDirectoryReader
from uchicagoldrtoolsuite.lib.structuring.stagingdirectorywriter import StagingDirectoryWriter
from uchicagoldrtoolsuite.lib.structuring.stagingdirectorywriter import StagingDirectoryWriter
from uchicagoldrtoolsuite.lib.structuring.segmentpackager import SegmentPackager
from uchicagoldrtoolsuite.lib.absolutefilepathtree import AbsoluteFilePathTree
from uchicagoldrtoolsuite.lib.structuring.externalstagingdirectorysegmentpackager import ExternalStagingDirectorySegmentPackager

__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    app = Stager(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class Stager(CLIApp):
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for moving materials into staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("--resume", "-r", help="An integer for a " +
                                 "run that needs to be resumed.",
                                 type=str, action='store', default=0)
        self.parser.add_argument("--group", "-g", help="The name of a group " +
                                 "to assign group ownership to the new " +
                                 "staging directory",
                                 type=str, action='store', default='None')
        self.parser.add_argument("directory", help="The directory that needs " +
                                 "to be staged.",
                                 type=str, action='store')
        self.parser.add_argument("numfiles", help="The number of files that " +
                                 "you are expecting to process",
                                 type=int, action='store')
        self.parser.add_argument("source_root", help="The root of the  " +
                                 "directory that needs to be staged.",
                                 type=str, action='store')
        self.parser.add_argument("destination_root", help="The location that " +
                                 "the staging directory should be created in",
                                 type=str, action='store')
        self.parser.add_argument("staging_id", help="The identifying name " +
                                 "for the new staging directory",
                                 type=str, action='store')
        self.parser.add_argument("prefix", help="The prefix defining the " +
                                 "type of run that is being processed",
                                 type=str, action='store')

        # Parse arguments into args namespace
        args = self.parser.parse_args()
        
        
        # App code
        
        staging_directory = join(args.destination_root, args.staging_id)
        staging_directory_reader = StagingDirectoryReader(staging_directory)
        staging_structure = staging_directory_reader.read()
        segment_ids = sorted([x.identifier for x in staging_structure.segment])        
        this_prefix_and_number_segment_ids = [x for x in segment_ids
                                              if args.prefix+args.resume in x]
        this_prefix_segment_ids = [x for x in segment_ids if args.prefix in x]
        remainder = []
 
        if len(this_prefix_and_number_segment_ids) > 0:
            tree = AbsoluteFilePathTree(args.directory)
            all_nodes = tree.get_nodes()
            relevant_segment = [x for x in staging_structure.segment 
                                if x.identifier == args.prefix+args.resume][0]
            partly_done = [x for x in list(chain(*[x.original
                                                   for x in relevant_segment.materialsuite]))]
            count = 0
            for n_partly_done_item in partly_done:
                already_staged_x = relpath(n_partly_done_item.item_name, args.destination_root)
                already_staged_x = already_staged_x.split(args.staging_id)[1]
                already_staged_x = already_staged_x.split(args.prefix+args.resume)
                matches_in_tree = [n for n in all_nodes
                                   if re.compile(already_staged_x[1]).search(n.identifier)]
                if len(matches_in_tree) > 0:
                    pass
                else:
                    remainder.append(n.identifier)
            current_segment_number = this_prefix_and_number_segment_ids[-1]
            
        elif len(this_prefix_segment_ids) > 0:
            tree = AbsoluteFilePathTree(args.directory)
            current_segment_number = int(re.compile('(\w{1,})(\d{1,})').\
                                         match(this_prefix_segment_ids[-1]).group(2)) + 1
        else:
            current_segment_number = 1
            
        segment_packager = ExternalStagingDirectorySegmentPackager(args.prefix, current_segment_number)
        segment = segment_packager.package(args.directory, remainder_files=remainder)
        print(segment)
        # new_segment = segment_packager.create_segment(selected_items=remainder)


if __name__ == "__main__":
    s = Stager()
    s.main()
