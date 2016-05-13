from os.path import join, dirname
from sys import stdout

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.filesystemstagewriter import FileSystemStageWriter
from ..lib.filesystemstagereader import FileSystemStageReader
from ..lib.externalfilesystemsegmentpackager import \
    ExternalFileSystemSegmentPackager


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
        self.parser.add_argument("directory", help="The directory that " +
                                 "needs to be staged.",
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
        self.parser.add_argument("--resume", "-r", help="An integer for a " +
                                 "run that needs to be resumed.",
                                 type=str, action='store', default=0)
        self.parser.add_argument("--source_root", help="The root of the  " +
                                 "directory that needs to be staged.",
                                 type=str, action='store',
                                 default=None)
        self.parser.add_argument("--filter-pattern", help="A regex to " +
                                 "use to exclude files whose paths match.",
                                 type=str, action='store',
                                 default=None)

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # App code
        stage = FileSystemStageReader(join(args.destination_root,
                                           args.staging_id)).read()
        if args.resume:
            seg_num = args.resume
        else:
            segment_ids = []
            for segment in stage.segment_list:
                segment_ids.append(segment.identifier)
            segment_ids = [x for x in segment_ids if
                           x.split("-")[0] == args.prefix]
            segment_nums = [x.split("-")[1] for x in segment_ids]
            segment_nums = [int(x) for x in segment_nums]
            segment_nums.sort()
            if segment_nums:
                seg_num = segment_nums[-1]+1
            else:
                seg_num = 1
        if args.source_root:
            root = args.source_root
        else:
            root = dirname(args.directory)

        ext_seg_packager = ExternalFileSystemSegmentPackager(
            args.directory,
            args.prefix,
            seg_num,
            root=root,
            filter_pattern=args.filter_pattern)

        stdout.write("Source: " + args.directory+"\n")
        stdout.write("Stage: " + join(args.destination_root, args.staging_id) +
                     "\n")
        stdout.write("Segment: " + args.prefix + "-" + str(seg_num) + "\n")
        seg = ext_seg_packager.package()
        stage.add_segment(seg)
        writer = FileSystemStageWriter(stage, args.destination_root)
        writer.write()
        stdout.write("Complete\n")


if __name__ == "__main__":
    s = Stager()
    s.main()
