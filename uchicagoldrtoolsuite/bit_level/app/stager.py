from os.path import join, dirname, relpath
from logging import getLogger
from re import compile as re_compile

from pypremis.lib import PremisRecord

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from uchicagoldrtoolsuite.core.lib.convenience import recursive_scandir, \
    TemporaryFilePath
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.externalreaders.externalfilesystemmaterialsuitereader import \
    ExternalFileSystemMaterialSuiteReader
from ..lib.writers.filesystemstagewriter import FileSystemMaterialSuiteWriter
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter
from ..lib.structures.stage import Stage


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
    app = Stager(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class Stager(CLIApp):
    """
    takes an external location and formats it's contents into the
    beginnings of a staging structure and writes that to disk.

    This stager iteration is serialization specific - it computes where
    the directory should be in the pairtree based FileSystemStageWriter
    serialization and writes things one MaterialSuite at a time - cleaning up
    after itself after each MaterialSuite. This eliminates the required for
    the staging machines tmp directory to be larger than any single segment.
    """
    @log_aware(log)
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for moving materials into staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        log.debug("Adding application specific cli app arguments")
        self.parser.add_argument("directory", help="The directory that " +
                                 "needs to be staged.",
                                 type=str, action='store')
        self.parser.add_argument("staging_id", help="The identifying name " +
                                 "for the new staging directory",
                                 type=str, action='store')
        self.parser.add_argument("--staging_env", help="The path to your " +
                                 "staging environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--resume", "-r", help="Resume a previously " +
                                 "started run.",
                                 action='store_true')
        self.parser.add_argument("--source_root", help="The root of the  " +
                                 "directory that needs to be staged.",
                                 type=str, action='store',
                                 default=None)
        self.parser.add_argument("--filter_pattern", help="Regexes to " +
                                 "use to exclude files whose rel paths match.",
                                 action='append', default=[])
        self.parser.add_argument("--eq_detect", help="The equality " +
                                 "metric to use on writing, check " +
                                 "LDRItemCopier for supported schemes.",
                                 type=str, action='store',
                                 default="bytes")
        self.parser.add_argument("--run_name", help="An optional name " +
                                 "for this run to be recorded in PREMIS " +
                                 "ingestion events for later querying.",
                                 type=str, action='store',
                                 default=None)

        # Parse arguments into args namespace
        args = self.parser.parse_args()
        self.process_universal_args(args)

        # App code
        if args.resume and not args.run_name:
            raise RuntimeError("In order to resume a run you must specify " +
                               "a run name")

        filter_patterns = [re_compile(x) for x in args.filter_pattern]

        if args.staging_env:
            destination_root = args.staging_env
        else:
            destination_root = self.conf.get("Paths",
                                             "staging_environment_path")
        destination_root = self.expand_path(destination_root)

        if args.source_root:
            root = args.source_root
        else:
            root = dirname(args.directory)
        root = self.expand_path(root)

        args.directory = self.expand_path(args.directory)

        log.info("Source: " + args.directory)
        log.info("Source Root: " + root)

        log.info("Reading Stage...")
        stage = FileSystemStageReader(destination_root, args.staging_id).read()

        log.info("Stage: " + join(destination_root, args.staging_id))

        _exists = []
        if args.resume:
            for ms in stage.materialsuite_list:
                try:
                    with TemporaryFilePath() as tmp_path:
                        with ms.premis.open() as src:
                            with open(tmp_path, 'wb') as dst:
                                dst.write(src.read())
                        premis = PremisRecord(frompath=tmp_path)
                        obj = premis.get_object_list()[0]
                        originalName = obj.get_originalName()
                        run_id = None
                        for event in premis.get_event_list():
                            for eventDetailInformation in \
                                    event.get_eventDetailInformation():
                                eventDetail = eventDetailInformation.get_eventDetail()
                                if eventDetail.startswith("Run Identifier"):
                                    run_id = eventDetail.split(": ")[1]
                        if run_id == args.run_name:
                            _exists.append(originalName)
                except Exception as e:
                    log.warn(
                        "An exception occured in resumption duplicate " +
                        "detection in MaterialSuite({})".format(
                            ms.identifier
                        ) +
                        "The Exception was: {}".format(str(e))
                    )
                    raise e
            _exists = set(_exists)

        log.info("Processing & Writing...")

        # We need a stage writer here just for the stage skeleton, we're going
        # to manually handle dealing with the nested writers so we can stage
        # things file by file rather than having to load the whole incoming
        # directory into the tmp dir
        stage_writer = FileSystemStageWriter(
            Stage(args.staging_id), destination_root
        )
        stage_writer._build_skeleton()
        computed_segment_path = join(
            destination_root, args.staging_id, 'pairtree_root'
        )

        for x in recursive_scandir(args.directory):
            if not x.is_file():
                continue
            _filter = False
            for f_patt in filter_patterns:
                if f_patt.fullmatch(relpath(x.path, root)):
                    log.debug(
                        "A filter pattern matched a file path, skipping. " +
                              "Pattern: {}, Path: {}".format(
                                  f_patt.pattern,
                                  relpath(x.path, root)
                              )
                    )
                    _filter = True
                    break
            if _filter:
                continue
            if args.resume:
                log.debug("Determining if the run name and relpath " +
                          "already exist in the stage")
                if relpath(x.path, root) in _exists:
                    log.debug(
                        "{} appears in the existing stage, skipping".format(
                             relpath(x.path, root)
                        )
                    )
                    continue
                else:
                    log.debug(
                        "{} does not appear in the existing stage, processing".format(
                            relpath(x.path, root)
                        )
                    )

            p = ExternalFileSystemMaterialSuiteReader(
                x.path, root=root, run_name=args.run_name
            )
            ms = p.read()
            w = FileSystemMaterialSuiteWriter(
                ms, computed_segment_path, eq_detect=args.eq_detect,
                encapsulation=stage_writer.encapsulation
            )
            w.write()
            del p

        log.info("Complete")


if __name__ == "__main__":
    s = Stager()
    s.main()
