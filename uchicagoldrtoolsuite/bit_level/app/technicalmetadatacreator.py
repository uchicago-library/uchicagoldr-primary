from sys import stdout
from os.path import join

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.filesystemstagewriter import FileSystemStageWriter
from ..lib.filesystemstagereader import FileSystemStageReader
from ..lib.generictechnicalmetadatacreator import \
    GenericTechnicalMetadataCreator


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
    app = TechnicalMetadataCreator(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class TechnicalMetadataCreator(CLIApp):
    """
    Creates technical metadata (FITs) for all the material suites in a stage.
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
        self.parser.add_argument("staging_env", help="The path to your " +
                                 "staging environment directory.")
        self.parser.add_argument("stage_id", help="The id of the stage",
                                 type=str, action='store')
        self.parser.add_argument("--skip-existing", help="Skip material " +
                                 "suites which already claim to have " +
                                 "technical metadata",
                                 action='store_true',
                                 default=False)

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # App code
        stage_fullpath = join(args.staging_env, args.stage_id)
        reader = FileSystemStageReader(stage_fullpath)
        stage = reader.read()
        stdout.write("Stage: " + stage_fullpath + "\n")

        techmd_creator = GenericTechnicalMetadataCreator(stage)
        techmd_creator.process(skip_existing=args.skip_existing)

        writer = FileSystemStageWriter(stage, args.staging_env)
        writer.write()
        stdout.write("Complete\n")


if __name__ == "__main__":
    s = TechnicalMetadataCreator()
    s.main()
