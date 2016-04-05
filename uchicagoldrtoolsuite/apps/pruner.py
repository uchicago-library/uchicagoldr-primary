from os.path import exists
from argparse import Action
from uchicagoldrtoolsuite.apps.internals.cliapp import CLIApp


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
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
    def __call__(self, parser, namespace, value, option_string=None):
        if not exists(value):
            print(value)
            raise IOError("{} does not exist on the filesystem")
        setattr(namespace, self.dest, value)


class Pruner(CLIApp):
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for pruning materials in staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__),
                          fromfile_prefix_chars='@')
        # Add application specific flags/arguments
        self.parser.add_argument("directory",
                                 help="Enter a valid directory that needs " +
                                 "to be pruned",
                                 action=ValidateDirectory)
        self.parser.add_argument("source_root",
                                 help="Enter the root of the directory",
                                 action=ValidateDirectory)
        self.parser.add_argument("patterns",
                                 help="Enter a list of regular " +
                                 "expressions matching file names that can " +
                                 "be deleted from the staging directory",
                                 action='store', nargs="*")
        # Parse arguments into args namespace
        args = self.parser.parse_args()
        # App code
        try:
            p = Pruner(args.directory, args.source_root, args.patterns)
            is_it_valid = p.validate()
            if is_it_valid:
                num_files_deleted = p.ingest()
                self.stdoutp("{} have been removed from {}\n".format(
                    str(num_files_deleted), args.directory))
            else:
                problem = p.explain_validation_result()
                self.stderrp("{}: {}\n".format(problem.category,
                                               problem.message))
            return 0
        except KeyboardInterrupt:
            return 131
