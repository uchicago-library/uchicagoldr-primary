from collections import namedtuple
from uchicagoldrtoolsuite.apps.internals import CLIApp
from uchicagoldrtoolsuite.lib.fileprocessor import FileProcessor

__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"

def launch():
    app = Archiver(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()

class Archiver(CLIApp):
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for moving materials into staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("directory", type=str, action='store')
        self.parser.add_argument("source_root", type=str, action='store')
        self.parser.add_argument("destination_root", type=int, action='store')
        self.parser.add_argument("numfiles", type=int, action='store')
        self.parser.add_argument("numfolders", type=int, action='store')
        # Parse arguments into args namespace
        args = self.parser.parse_args()
        fp = FileProcessor(args.directory, 'archiving', namedtuple("DirectoryInfo",
                                                    "src_root dest_root directory_id prefix " +\
                                                    "directory_type resume group_name validation")
                        (args.source_root, args.destination_root, args.staging_id,
                            args.prefix, 'archiving', args.resume,
                            args.group,
                            {'numfiles':args.numfiles, 'numfolders':args.numfolders}))
        fp.move()

