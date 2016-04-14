from os.path import join
import sys
sys.path.append("../lib/uchicagoldrtoolsuite")
sys.path.append(".")
from uchicagoldrtoolsuite.apps.internals.cliapp import CLIApp
from uchicagoldrtoolsuite.lib.structuring.stagingdirectoryreader import StagingDirectoryReader


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
                                 type=int, action='store', default=0)
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
        stagingreader = StagingDirectoryReader(args.destination_root,
args.source_root, join(args.directory, args.staging_id))
        print(stagingreader)
        stagingreader.gather_resources(args.directory)
if __name__ == "__main__":
    s = Stager()
    s.main()
