from os.path import join
import re
from itertools import chain
from os.path import relpath

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.filesystemstagewriter import FileSystemStageWriter
from ..lib.filesystemstagereader import FileSystemStageReader
from ..lib.absolutefilepathtree import AbsoluteFilePathTree
from ..lib.filesystemsegmentpackager import FileSystemSegmentPackager


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    """
    entry point launch hook
    """
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
    """
    takes an external location and formats it's contents into the
    beginnings of a staging structure and writes that to disk.
    """
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
        self.parser.add_argument("directory", help="The directory that " +
                                 "needs to be staged.",
                                 type=str, action='store')
        self.parser.add_argument("source_root", help="The root of the  " +
                                 "directory that needs to be staged.",
                                 type=str, action='store')
        self.parser.add_argument("destination_root", help="The location " +
                                 "that the staging directory should be " +
                                 "created in",
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
        staging_directory_reader = FileSystemStageReader(staging_directory)
        staging_structure = staging_directory_reader.read()

        segment_ids = sorted([x.identifier for x in staging_structure.segment])
        this_prefix_and_number_segment_ids = [x for x in segment_ids
                                              if args.prefix+'-'+str(args.resume)
                                              in x]
        this_prefix_segment_ids = [x for x in segment_ids if args.prefix in x]
        remainder = []

        if len(this_prefix_and_number_segment_ids) > 0:
            tree = AbsoluteFilePathTree(args.directory)
            all_nodes = tree.get_files()
            relevant_segment = [x for x in staging_structure.segment
                                if x.identifier == args.prefix + '-' +
                                args.resume][0]
            partly_done = [x for x in list(chain(*[x.original
                                                   for x in relevant_segment.
                                                   materialsuite]))]

            for n_origin_item in all_nodes:
                n_identifier = '.*'+relpath(n_origin_item,
                                            args.source_root) + '$'
                match_pattern = re.compile(r'%s' % n_identifier)
                matches = [x.item_name for x in partly_done
                           if match_pattern.match(x.item_name)]
                if len(matches) == 0:
                    remainder.append(n_origin_item)
                else:
                    pass
            current_segment_number = args.resume
        elif len(this_prefix_segment_ids) > 0:
            tree = AbsoluteFilePathTree(args.directory)
            match_pattern = re.compile('(\w{1,})[-](\d{1,2})')
            segment_numbers = [int(re.compile('(\w{1,})[-](\d{1,})').
                                   match(x).group(2))
                               for x in this_prefix_segment_ids]
            current_segment_number = sorted(segment_numbers)[-1] + 1
        else:
            current_segment_number = 1

        segment_packager = FileSystemSegmentPackager(
            args.prefix,
            current_segment_number)
        segment = segment_packager.package(args.directory,
                                           remainder_files=remainder)

        staging_structure.segment.append(segment)

        staging_directory_writer = FileSystemStageWriter(staging_structure)
        staging_directory_writer.write(join(args.destination_root,
                                            args.staging_id),
                                       args.source_root)


if __name__ == "__main__":
    s = Stager()
    s.main()
