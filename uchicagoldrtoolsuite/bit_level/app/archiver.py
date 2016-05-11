from uuid import uuid1

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.filesystemstagereader import FileSystemStageReader
from ..lib.filesystemarchivestructurewriter import \
    FileSystemArchiveStructureWriter


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    """
    launch hook for entry point
    """
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
    """
    This application reads a complete staging directory, translates the
    resulting Staging Structure into an Archive Structure and writes that
    Archive Structure to a location.
    """
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
        self.parser.add_argument("destination_root", type=str, action='store')

        # Parse arguments into args namespace
        args = self.parser.parse_args()
        staging_reader = FileSystemStageReader(args.directory)
        staging_structure = staging_reader.read()
        writer = FileSystemArchiveStructureWriter(staging_structure,
                                                  args.destination_root)

        #writer.write()


if __name__ == "__main__":
    a = Archiver()
    a.main()
