from os.path import join, dirname, expanduser, expandvars
from logging import getLogger

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from uchicagoldrtoolsuite.core.lib.convenience import recursive_scandir
from uchicagoldrtoolsuite import \
    activate_master_log_file, \
    activate_job_log_file, \
    activate_stdout_log
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.externalpackagers.externalfilesystemmaterialsuitepackager import \
    ExternalFileSystemMaterialSuitePackager
from ..lib.writers.filesystemstagewriter import FileSystemMaterialSuiteWriter


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)
activate_master_log_file()
activate_job_log_file()


def launch():
    """
    entry point launch hook
    """
    app = PiecemealStager(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class PiecemealStager(CLIApp):
    """
    takes an external location and formats it's contents into the
    beginnings of a staging structure and writes that to disk.

    This stager iteration is serialization specific - it computes where
    the directory should be in the pairtree based FileSystemStageWriter
    serialization and writes things one MaterialSuite at a time - cleaning up
    after itself after each MaterialSuite. This eliminates the required for
    the staging machines tmp directory to be larger than any single segment.
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for moving materials into staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("directory", help="The directory that " +
                                 "needs to be staged.",
                                 type=str, action='store')
        self.parser.add_argument("staging_id", help="The identifying name " +
                                 "for the new staging directory",
                                 type=str, action='store')
        self.parser.add_argument("prefix", help="The prefix defining the " +
                                 "type of run that is being processed",
                                 type=str, action='store')
        self.parser.add_argument("--staging_env", help="The path to your " +
                                 "staging environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--resume", "-r", help="An integer for a " +
                                 "run that needs to be resumed.",
                                 type=str, action='store', default=0)
        self.parser.add_argument("--source_root", help="The root of the  " +
                                 "directory that needs to be staged.",
                                 type=str, action='store',
                                 default=None)
        self.parser.add_argument("--filter_pattern", help="A regex to " +
                                 "use to exclude files whose paths match.",
                                 type=str, action='store',
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
            destination_root = args.staging_env
        else:
            destination_root = self.conf.get("Paths",
                                             "staging_environment_path")

        if args.source_root:
            root = args.source_root
        else:
            root = dirname(args.directory)

        destination_root = expandvars(expanduser(destination_root))
        args.directory = expandvars(expanduser(args.directory))

        log.info("Source: " + args.directory)
        log.info("Source Root: " + root)

        log.info("Reading Stage...")
        stage = FileSystemStageReader(join(destination_root,
                                           args.staging_id)).read()

        log.info("Stage: " + join(destination_root, args.staging_id))

        if args.resume:
            seg_num = args.resume
        else:
            segment_ids = []
            for segment in stage.segment_list:
                segment_ids.append(segment.identifier)
            segment_ids = [x for x in segment_ids if
                           x.split("-")[0] == args.prefix]
            segment_nums = [x.split("-")[1] for x in segment_ids]
            segment_nums = [int(x) for x in segment_nums]
            segment_nums.sort()
            if segment_nums:
                seg_num = segment_nums[-1]+1
            else:
                seg_num = 1

        log.info("Segment: " + args.prefix + "-" + str(seg_num))

        log.info("Processing...")
        log.info("Writing...")

        computed_segment_path = join(
            destination_root, args.staging_id, 'segments',
            args.prefix + "-" + str(seg_num)
        )

        for x in recursive_scandir(args.directory):
            if not x.is_file():
                continue
            p = ExternalFileSystemMaterialSuitePackager(x.path, root=root)
            ms = p.package()
            w = FileSystemMaterialSuiteWriter(
                ms, computed_segment_path, eq_detect=args.eq_detect
            )
            w.write()
            del p

        log.info("Complete")


if __name__ == "__main__":
    s = PiecemealStager()
    s.main()
