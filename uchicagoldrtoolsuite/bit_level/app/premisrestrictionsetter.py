from os.path import join
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.processors.genericpremisrestrictionsetter import \
    GenericPREMISRestrictionSetter


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
    app = PremisRestrictionSetter(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class PremisRestrictionSetter(CLIApp):
    """
    Sets restrictions in PREMIS records
    """
    @log_aware(log)
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for setting restrictions in PREMIS metadata " +
                          "records in a stage.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        log.debug("Adding application specific cli app arguments")
        self.parser.add_argument("stage_id", help="The stage identifier",
                                 type=str, action='store')
        self.parser.add_argument("restriction", help="The restriction to set.",
                                 type=str, action='store')
        self.parser.add_argument("--reason", help="The reason for setting " +
                                 "this restriction",
                                 action="append")
        self.parser.add_argument("--donor_stipulation", help="A donor " +
                                 "stipulation pertaining to this restriction.",
                                 action="append")
        self.parser.add_argument("--linking_agentid", help="Any linking " +
                                 "agent identifiers pertaining to this " +
                                 "restriction.",
                                 action="append")
        self.parser.add_argument("--inactive", help="Use this flag to set a " +
                                 "restriction to inactive when it is added.",
                                 action="store_true",
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
        self.process_universal_args(args)

        # App code

        if args.staging_env:
            staging_env = args.staging_env
        else:
            staging_env = self.conf.get("Paths", "staging_environment_path")
        staging_env = self.expand_path(staging_env)

        reader = FileSystemStageReader(staging_env, args.stage_id)
        stage = reader.read()
        log.info("Stage: " + join(staging_env, args.stage_id))

        log.info("Processing...")

        premis_restriction_setter = GenericPREMISRestrictionSetter(
            stage,
            args.restriction,
            args.reason,
            args.donor_stipulation,
            args.linking_agentid,
            not args.inactive
        )
        premis_restriction_setter.process()

        log.info("Writing...")
        writer = FileSystemStageWriter(stage, staging_env,
                                       eq_detect=args.eq_detect)
        writer.write()
        log.info("Complete")


if __name__ == "__main__":
    s = PremisRestrictionSetter()
    s.main()
