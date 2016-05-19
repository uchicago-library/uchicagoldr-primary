from sys import stdout
from os.path import join

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.filesystemstagewriter import FileSystemStageWriter
from ..lib.filesystemstagereader import FileSystemStageReader
from ..lib.genericpresformcreator import \
    GenericPresformCreator
from ..lib.converters.officetopdfconverter import OfficeToPDFConverter
from ..lib.converters.officetocsvconverter import OfficeToCSVConverter
from ..lib.converters.officetotxtconverter import OfficeToTXTConverter
from ..lib.converters.videoconverter import VideoConverter
from ..lib.converters.imageconverter import ImageConverter
from ..lib.converters.audioconverter import AudioConverter


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
    app = PresformCreator(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class PresformCreator(CLIApp):
    """
    Creates PRESFORM files for the contents of a stage
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for creating presforms for materials in " +
                          "a stage.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("staging_env", help="The path to your " +
                                 "staging environment directory.")
        self.parser.add_argument("stage_id", help="The id of the stage",
                                 type=str, action='store')
        self.parser.add_argument("--skip-existing", help="Skip material " +
                                 "suites which already claim to have " +
                                 "at least one presform",
                                 action='store_true',
                                 default=False)

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # App code
        stage_fullpath = join(args.staging_env, args.stage_id)
        reader = FileSystemStageReader(stage_fullpath)
        stage = reader.read()
        stdout.write("Stage: " + stage_fullpath + "\n")

        converters = [
            OfficeToPDFConverter,
            OfficeToCSVConverter,
            OfficeToTXTConverter,
            VideoConverter,
            ImageConverter,
            AudioConverter
        ]

        presform_creator = GenericPresformCreator(stage, converters)
        presform_creator.process(skip_existing=args.skip_existing)

        writer = FileSystemStageWriter(stage, args.staging_env)
        writer.write()
        stdout.write("Complete\n")


if __name__ == "__main__":
    s = PresformCreator()
    s.main()
