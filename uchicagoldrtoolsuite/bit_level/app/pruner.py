from argparse import Action
from logging import getLogger
from os.path import exists, join
from re import compile as re_compile
from json import dumps

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.processors.genericpruner import GenericPruner
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


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
        self.parser.add_argument('--final_decision',
                                 help="A flag to set when you really want to" +
                                 " delete the files matching the pattern",
                                 default=False, action='store_true')
        self.parser.add_argument("stage_id",
                                 help="Enter a valid directory that needs " +
                                 "to be pruned",
                                 action='store')
        self.parser.add_argument("selection_patterns",
                                 help="Enter a list of regular " +
                                 "expressions matching file names that can " +
                                 "be deleted from the staging directory",
                                 action='store', nargs="*")
        self.parser.add_argument("--staging_env", help="The path to your " +
                                 "staging environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--exclusion_pattern",
                                 help="Specify a list of patterns which" +
                                 "'save' an item whose item name matches " +
                                 "a deletion pattern from being removed.",
                                 action='append', default=[])
        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # Set conf
        self.set_conf(conf_dir=args.conf_dir, conf_filename=args.conf_file)

        # App code

        if args.staging_env:
            staging_env = args.staging_env
        else:
            staging_env = self.conf.get("Paths", "staging_environment_path")

        stage_fullpath = join(staging_env, args.stage_id)
        staging_directory_reader = FileSystemStageReader(stage_fullpath)
        staging_structure = staging_directory_reader.read()
        try:
            p = GenericPruner(staging_structure,
                              callback_args=[[re_compile(x) for x in args.selection_patterns]],
                              callback_kwargs={'exclude_patterns': [re_compile(x) for x in args.exclusion_pattern]},
                              final=args.final_decision, in_place_delete=True)
            r = p.prune()
            print(dumps(r, indent=4))
            w = FileSystemStageWriter(staging_structure, staging_env,
                                      eq_detect="adler32")
            w.write()
        except KeyboardInterrupt:
            return 131


if __name__ == "__main__":
    p = Pruner()
    p.main()
