from sys import stdout
from logging import getLogger
from os.path import join
from tempfile import TemporaryDirectory
from uuid import uuid1

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
fromuchicagoldrtoolsuite import \
    activate_master_log_file, \
    activate_job_log_file, \
    activate_stdout_log
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
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
    app = AccessionRecordAdder(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class AccessionRecordAdder(CLIApp):
    """
    Create an accession record in a Stage
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="Adds a file as an accession record " +
                          "to a stage. ",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("stage_id", help="The id of the stage",
                                 type=str, action='store')
        group = self.parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--file",
                           help='Add a file as a note',
                           action='store_true',
                           default=False)
        group.add_argument("--text",
                           help='Add text as a note',
                           action='store_true',
                           default=False)
        self.parser.add_argument("note_title",
                                 type=str,
                                 action='store',
                                 help="What the note will be titled in the " +
                                 "stage.")
        self.parser.add_argument("note",
                                 type=str,
                                 action='store',
                                 help="Either a file path if you specified " +
                                 "--file or a string of text enclosed in " +
                                 "quotes if you specified --text")
        self.parser.add_argument("--staging_env", help="The path to your " +
                                 "staging environment directory.",
                                 type=str,
                                 action='store',
                                 default=None)
        self.parser.add_argument("--eq_detect", help="The equality " +
                                 "metric to use on writing, check " +
                                 "LDRItemCopier for supported schemes.",
                                 type=str, action='store',
                                 default="bytes")

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        activate_stdout_log(args.verbosity)

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

        if args.file:
            x = LDRPath(args.note)
            x.set_name(args.note_title)
            stage.add_accessionrecord(x)
        elif args.text:
            tmpdir = TemporaryDirectory()
            text_file_path = join(tmpdir.name, str(uuid1()))
            with open(text_file_path, 'a') as f:
                f.write(args.note)
                f.write('\n')
            x = LDRPath(text_file_path)
            x.set_name(args.note_title)
            stage.add_accessionrecord(x)
        else:
            raise AssertionError('Either file or text should be selected')

        log.info("Writing...")
        writer = FileSystemStageWriter(stage, staging_env, eq_detect=args.eq_detect)
        writer.write()
        log.info("Complete")


if __name__ == "__main__":
    s = AccessionRecordAdder()
    s.main()
