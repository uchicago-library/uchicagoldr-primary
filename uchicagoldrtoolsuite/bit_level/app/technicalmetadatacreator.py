from sys import stdout
from logging import getLogger
from os.path import join
from configparser import NoOptionError

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.processors.generictechnicalmetadatacreator import \
    GenericTechnicalMetadataCreator
from ..lib.techmdcreators.fitscreator import FITsCreator
from ..lib.techmdcreators.apifitscreator import APIFITsCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


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
        self.parser.add_argument("--skip_existing", help="Skip material " +
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
        self.parser.add_argument("--fits_path", help="The path to the FITS " +
                                 "executable on this system. " +
                                 "Overrides any value found in configs.",
                                 type=str, action='store',
                                 default=None)
        self.parser.add_argument("--fits_api_url", help="The url of a FITS " +
                                 "Servlet examine endpoint. " +
                                 "Overrides any value found in configs.",
                                 type=str, action='store',
                                 default=None)
        self.parser.add_argument("--use_api", help="Use a FITS Servlet " +
                                 "instead of a local FITS install.",
                                 action="store_true",
                                 default=False)

        # Parse arguments into args namespace
        args = self.parser.parse_args()
        self.process_universal_args(args)

        # App code

        if args.staging_env:
            staging_env = args.staging_env
        else:
            staging_env = self.conf.get("Paths", "staging_environment_path")

        dto = {}
        try:
            dto['fits_path'] = self.conf.get("Paths", "fits_path")
        except NoOptionError:
            pass
        try:
            dto['fits_api_url'] = self.conf.get("URLs", "fits_api_url")
        except NoOptionError:
            pass


        if args.fits_api_url is not None:
            dto['fits_api_url'] = args.fits_api_url
        if args.fits_path is not None:
            dto['fits_path'] = args.fits_path

        stage_fullpath = join(staging_env, args.stage_id)
        reader = FileSystemStageReader(stage_fullpath)
        stage = reader.read()
        log.info("Stage: " + stage_fullpath)

        log.info("Processing...")

        if args.use_api:
            techmd_processors = [APIFITsCreator]
        else:
            techmd_processors = [FITsCreator]

        techmd_creator = GenericTechnicalMetadataCreator(stage,
                                                         techmd_processors)
        techmd_creator.process(skip_existing=args.skip_existing,
                               data_transfer_obj=dto)

        log.info("Writing...")
        writer = FileSystemStageWriter(stage, staging_env, eq_detect=args.eq_detect)
        writer.write()
        log.info("Complete")


if __name__ == "__main__":
    s = TechnicalMetadataCreator()
    s.main()
