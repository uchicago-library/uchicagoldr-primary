from sys import stdout

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.filesystemstagewriter import FileSystemStageWriter
from ..lib.filesystemstagereader import FileSystemStageReader
from ..lib.genericpremiscreator import GenericPREMISCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    """
    entry point launch hook
    """
    app = PremisCreator(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class PremisCreator(CLIApp):
    """
    Creates PREMIS object records for all the material suites in a stage.
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "creating technical metadata for materials in " +
                          "a stage.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("directory", help="The directory containing " +
                                 "the serialized stage.",
                                 type=str, action='store')
        self.parser.add_argument("--skip-existing", help="Skip material " +
                                 "suites which already claim to have " +
                                 "premis records",
                                 type=bool, action='store_true',
                                 default=False)

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # App code
        stage = FileSystemStageReader(args.directory)
        stdout.write(args.directory)

        premis_creator = GenericPREMISCreator(stage)
        premis_creator.process(skip_existing=args.skip_existing)

        writer = FileSystemStageWriter(stage, args.directory)
        writer.write()
        stdout.write("Complete")


if __name__ == "__main__":
    s = PremisCreator()
    s.main()
