from argparse import Action
from os.path import exists
import re
from sys import stdout

from uchicagoldrtoolsuite.apps.internals.cliapp import CLIApp
from uchicagoldrtoolsuite.lib.structuring.stagingdirectoryreader import \
    StagingDirectoryReader


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    """
    entry_point launch hook
    """
    app = Pruner(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class ValidateDirectory(Action):
    """
    Argparse Action class for determining a directory exists
    when passed as an argument
    """
    def __call__(self, parser, namespace, value, option_string=None):
        if not exists(value):
            print(value)
            raise IOError("{} does not exist on the filesystem")
        setattr(namespace, self.dest, value)


class Pruner(CLIApp):
    """
    Looks through staging directories for files whose names match
    a given set of patterns and removes them if they do
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for pruning materials in staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__),
                          fromfile_prefix_chars='@')
        # Add application specific flags/arguments
        self.parser.add_argument('--final_decision', type=bool,
                                 help="A flag to set when you really want to" +
                                 " delete the files matching the pattern",
                                 default=False)
        self.parser.add_argument("directory",
                                 help="Enter a valid directory that needs " +
                                 "to be pruned",
                                 action=ValidateDirectory)
        self.parser.add_argument("patterns",
                                 help="Enter a list of regular " +
                                 "expressions matching file names that can " +
                                 "be deleted from the staging directory",
                                 action='store', nargs="*")
        # Parse arguments into args namespace
        args = self.parser.parse_args()
        # App code
        staging_directory_reader = StagingDirectoryReader(args.directory)
        staging_structure = staging_directory_reader.read()
        try:
            for n_segment in staging_structure.segment:
                for n_suite in n_segment.materialsuite:
                    for req_part in n_suite.required_parts:
                        if isinstance(getattr(n_suite, req_part), list):
                            for n_file in getattr(n_suite, req_part):
                                for pattern in args.patterns:
                                    match_pattern = re.compile(pattern)
                                    if match_pattern.match(n_file.item_name):
                                        success, message = n_file.delete(
                                            final=args.final_decision
                                        )
                                        stdout.write("{}\n".format(message))

            return 0
        except KeyboardInterrupt:
            return 131


if __name__ == "__main__":
    p = Pruner()
    p.main()
