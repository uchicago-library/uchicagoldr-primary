
from grp import getgrnam
from os import chmod, chown
from os.path import join
from pwd import getpwnam
from sys import stdout

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder

from ..lib.fstools.absolutefilepathtree import AbsoluteFilePathTree
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.writers.filesystemarchivewriter import FileSystemArchiveWriter
from ..lib.transformers.stagetoarchivetransformer import StageToArchiveTransformer

__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    """
    launch hook for entry point
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
    This application reads a complete staging directory, translates the
    resulting Staging Structure into an Archive Structure and writes that
    Archive Structure to a location.
    """

    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for moving materials into the archive.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("directory", type=str, action='store',
                                 help="Enter the stage directory that is" +
                                 " ready to be archived")
        self.parser.add_argument("origin_root", type=str, action='store',
                                 help="Enter the root of the directory " +
                                 "entered")
        self.parser.add_argument("--archive", type=str, action='store',
                                 help="Use this to specify a non-default " +
                                 "archive location",
                                 default="/data/repository/archive")
        self.parser.add_argument("--group", type=str, action='store',
                                 help="Enter the name of the group that" +
                                 " should own the files in the archive.", default="repository")
        self.parser.add_argument("--user", type=str, action='store',
                                 help="Enter the name of the user who " +
                                 "should own the files in the archive.", default="repository")
        self.parser.add_argument(
            "--dry-run", help="Use this flag if you don't actually want to " +
            "change ownership of the files", action='store_true', default=False)
        # Parse arguments into args namespace
        args = self.parser.parse_args()
        staging_reader = FileSystemStageReader(args.directory)
        staging_structure = staging_reader.read()
        transformer = StageToArchiveTransformer(staging_structure)
        id_type, identifier = IDBuilder().build('premisID').show()
        archive_structure = transformer.transform(defined_id=identifier)
        writer = FileSystemArchiveWriter(archive_structure, args.archive,
                                         args.directory)
        writer.write()
        stdout.write("new arf located at {}\n".format(
            join(writer.archive_loc,
                 writer.pairtree.get_pairtree_path())))
        file_tree = AbsoluteFilePathTree(
            join(args.archive, writer.pairtree.get_pairtree_path()))

        if not args.dry_run:
            gid = getpwnam(args.user).pw_uid
            uid = getgrnam(args.group).gr_gid
            for f in file_tree:
                if len(f.split('pairtree_root')) <= 1:
                    pass
                else:
                    chown(f, uid, gid)
                    chmod(f, 0x0750)

if __name__ == "__main__":
    a = Archiver()
    a.main()
