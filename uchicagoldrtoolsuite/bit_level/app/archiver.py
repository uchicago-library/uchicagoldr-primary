from os.path import join
from logging import getLogger

from pypairtree.utils import identifier_to_path

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
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


log = getLogger(__name__)


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
    @log_aware(log)
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for moving materials into archive structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        log.debug("Adding application specific cli app arguments")
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
        self.parser.add_argument("--eq_detect", help="The equality " +
                                 "metric to use on writing, check " +
                                 "LDRItemCopier for supported schemes.",
                                 type=str, action='store',
                                 default="bytes")
        self.parser.add_argument("--noid_minter_url", help="Manually specify " +
                                 "the url of the noid minter to use. " +
                                 "Defaults to the config value.",
                                 type=str, action='store')
        self.parser.add_argument("--lts_identifier", help="Manually specify " +
                                 "the identifier to use for the Archive " +
                                 "structure. Overrides noid minter urls.",
                                 type=str, action='store',
                                 default=None)

        # Parse arguments into args namespace
        args = self.parser.parse_args()
        self.process_universal_args(args)

        # App code

        if args.staging_env:
            staging_env = args.staging_env
        else:
            staging_env = self.conf.get("Paths", "staging_environment_path")
        staging_env = self.expand_path(staging_env)

        if args.lts_env:
            lts_env = args.lts_env
        else:
            lts_env = self.conf.get("Paths",
                                    "long_term_storage_environment_path")
        lts_env = self.expand_path(lts_env)

        if args.noid_minter_url:
            noid_minter_url = args.noid_minter_url
        else:
            noid_minter_url = self.conf.get("URLs", "noid_minter")

        log.info("Stage Path: {}".format(join(staging_env, args.stage_id)))
        log.info("Reading Stage...")
        stage = FileSystemStageReader(staging_env, args.stage_id).read()
        log.info("Transforming Stage into Archive")
        archive = StageToArchiveTransformer(stage).transform(
            noid_minter_url=noid_minter_url,
            archive_identifier=args.lts_identifier
        )
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
        FileSystemArchiveWriter(archive, lts_env, args.eq_detect).write()
        log.info("Complete!")

if __name__ == "__main__":
    s = Archiver()
    s.main()
