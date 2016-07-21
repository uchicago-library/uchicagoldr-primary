from sys import stdout
from os.path import join

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.processors.generictechnicalmetadatacreator import \
    GenericTechnicalMetadataCreator
from ..lib.techmdcreators.fitscreator import FITsCreator


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
        self.parser.add_argument("stage_id", help="The id of the stage",
                                 type=str, action='store')
        self.parser.add_argument("--skip-existing", help="Skip material " +
                                 "suites which already claim to have " +
                                 "technical metadata",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--staging_env", help="The path to your " +
                                 "staging environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--eq_detect", help="The equality " +
                                 "metric to use on writing, check " +
                                 "LDRItemCopier for supported schemes.",
                                 type=str, action='store',
                                 default="bytes")

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # Set conf
        self.set_conf(conf_dir=args.conf_dir, conf_filename=args.conf_file)

        # App code

        if args.staging_env:
            staging_env = args.staging_env
        else:
            staging_env = self.conf.get("Paths", "staging_environment_path")

        stage_fullpath = join(staging_env, args.stage_id)
        reader = FileSystemStageReader(stage_fullpath)
        stage = reader.read()
        stdout.write("Stage: " + stage_fullpath + "\n")

        stdout.write("Processing...\n")

        techmd_processors = [FITsCreator]
        techmd_creator = GenericTechnicalMetadataCreator(stage,
                                                         techmd_processors)
        techmd_creator.process(skip_existing=args.skip_existing)

        writer = FileSystemStageWriter(stage, staging_env, eq_detect=args.eq_detect)
        writer.write()
        stdout.write("Complete\n")


if __name__ == "__main__":
    s = TechnicalMetadataCreator()
    s.main()
