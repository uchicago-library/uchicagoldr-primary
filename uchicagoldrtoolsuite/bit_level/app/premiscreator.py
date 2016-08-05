from os.path import join

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.processors.genericpremiscreator import GenericPREMISCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


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
        self.parser.add_argument("stage_id", help="The stage identifier",
                                 type=str, action='store')
        self.parser.add_argument("--skip-existing", help="Skip material " +
                                 "suites which already claim to have " +
                                 "premis records",
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
        log.info("Stage: " + stage_fullpath)

        log.info("Processing...")

        premis_creator = GenericPREMISCreator(stage)
        premis_creator.process(skip_existing=args.skip_existing)

        writer = FileSystemStageWriter(stage, staging_env, eq_detect=args.eq_detect)
        writer.write()
        log.info("Complete")


if __name__ == "__main__":
    s = PremisCreator()
    s.main()
