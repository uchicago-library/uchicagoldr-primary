from os.path import join, dirname, expanduser, expandvars

from pypairtree.utils import identifier_to_path

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from uchicagoldrtoolsuite.core.lib.masterlog import \
    spawn_logger, \
    activate_master_log_file, \
    activate_job_log_file, \
    activate_stdout_log
from ..lib.writers.filesystemarchivewriter import FileSystemArchiveWriter
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.transformers.stagetoarchivetransformer import \
    StageToArchiveTransformer


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)
activate_master_log_file()
activate_job_log_file()


def launch():
    """
    entry point launch hook
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
    takes an external location and formats it's contents into the
    beginnings of a staging structure and writes that to disk.
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for moving materials into archive structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("stage_id", help="The identifying name " +
                                 "for the new staging directory",
                                 type=str, action='store')
        self.parser.add_argument("--staging_env", help="The path to your " +
                                 "staging environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--lts_env", help="The path to your " +
                                 "long term storage environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--live_premis_env", help="The path to your " +
                                 "live PREMIS environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--eq_detect", help="The equality " +
                                 "metric to use on writing, check " +
                                 "LDRItemCopier for supported schemes.",
                                 type=str, action='store',
                                 default="bytes")

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # Fire a stdout handler at our preferred verbosity
        activate_stdout_log(args.verbosity)

        # Set conf
        self.set_conf(conf_dir=args.conf_dir, conf_filename=args.conf_file)

        # App code

        if args.staging_env:
            staging_env = args.staging_env
        else:
            staging_env = self.conf.get("Paths", "staging_environment_path")

        if args.lts_env:
            lts_env = args.lts_env
        else:
            lts_env = self.conf.get("Paths",
                                    "long_term_storage_environment_path")

        if args.live_premis_env:
            live_premis_env = args.live_premis_env
        else:
            live_premis_env = self.conf.get("Paths",
                                            "live_premis_environment_path")

        stage_path = join(staging_env, args.stage_id)
        log.info("Stage Path: {}".format(stage_path))
        log.info("Reading Stage...")
        stage = FileSystemStageReader(stage_path).read()
        log.info("Transforming Stage into Archive")
        archive = StageToArchiveTransformer(stage).transform()
        log.info("Validating Archive...")
        if not archive.validate():
            log.critical("Invalid Archive! Aborting!")
            raise ValueError("Invalid Archive! Aborting!")
        log.info(
            "Archive Path: {}".format(
                identifier_to_path(archive.identifier, root=lts_env)
            )
        )
        log.info("Writing Archive...")
        FileSystemArchiveWriter(archive, lts_env, live_premis_env,
                                args.eq_detect).write()
        log.info("Complete!")

if __name__ == "__main__":
    s = Archiver()
    s.main()
