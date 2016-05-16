from sys import stdout
from os.path import join
from tempfile import TemporaryDirectory
from uuid import uuid1

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.filesystemstagewriter import FileSystemStageWriter
from ..lib.filesystemstagereader import FileSystemStageReader
from ..lib.ldrpath import LDRPath


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
    app = LegalNoteAdder(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class LegalNoteAdder(CLIApp):
    """
    Create a legal note in a Stage
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="Adds a file as a legal " +
                          "note to a stage. ",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("staging_env", help="The path to your " +
                                 "staging environment directory.")
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

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # App code
        stage_fullpath = join(args.staging_env, args.stage_id)
        reader = FileSystemStageReader(stage_fullpath)
        stage = reader.read()
        stdout.write("Stage: " + stage_fullpath + "\n")

        if args.file:
            x = LDRPath(args.note)
            x.set_name(args.note_title)
            stage.add_legalnote(x)
        elif args.text:
            tmpdir = TemporaryDirectory()
            text_file_path = join(tmpdir.name, str(uuid1()))
            with open(text_file_path, 'a') as f:
                f.write(args.note)
                f.write('\n')
            x = LDRPath(text_file_path)
            x.set_name(args.note_title)
            stage.add_legalnote(x)
        else:
            raise AssertionError('Either file or text should be selected')

        writer = FileSystemStageWriter(stage, args.staging_env)
        writer.write()
        stdout.write("Complete\n")


if __name__ == "__main__":
    s = LegalNoteAdder()
    s.main()
