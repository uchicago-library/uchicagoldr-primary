from os.path import isdir, split, join, abspath
from os import makedirs

from uchicagoldrtoolsuite.lib.premisobjectrecordcreator import \
    PremisObjectRecordCreator
from uchicagoldrtoolsuite.lib.stagereader import StageReader
from uchicagoldrtoolsuite.lib.rootedpath import RootedPath
from uchicagoldrtoolsuite.apps.internals.cliapp import CLIApp


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    """
    the hook for setuptools console_scripts
    """
    app = PremisObjectCreator(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


def write_records(records):
    """
    write a stack of records to disk

    __Args__

    1. records (list): A list of tuples formatted as:
        (PremisRecord instance, filepath)
    """
    while records:
        x = records.pop()
        target_path = x[1]
        record = x[0]
        if not isdir(split(target_path)[0]):
            makedirs(split(target_path)[0])
        record.write_to_file(target_path)


def build_record(path):
    """
    build a populated LDR premis record from a file on disk

    __Args__

    1. path (str): an abspath to a file to build a record for

    __Returns__

    * (PremisRecord): the built PREMIS record
    """
    return PremisObjectRecordCreator(path).get_record()


def build_stage_reader(path, root):
    """
    build a stage reader from a path

    __Args__

    1. path (str): the fullpath to a staging dir
    2. root(str): the rootpath for the staging dir
        - the arg parser handles setting root to None if left blank

    __Returns__

    * (StageReader): The built StageReader for the path
    """
    rooted_path = RootedPath(path, root=root)
    stage_reader = StageReader(rooted_path)
    return stage_reader


class PremisObjectCreator(CLIApp):
    """
    The CLI script for creating PREMIS records for staged contents
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for creating original PREMIS object records " +
                          "for materials in staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument(
            'path',
            help='Specify the path to the staging id'
        )

        self.parser.add_argument(
            '-r', '--root',
            default=None,
            help='Specify the root path for the staging directory, if not ' +
            'the immediate containing directory.'
        )

        self.parser.add_argument(
            '--batch-size',
            type=int,
            default=0,
            help='The maximum batch to store before writing into the staging ' +
            'environment. Set to 0 for no maximum batch size.'
        )

        self.parser.add_argument(
            '--overwrite',
            default=False,
            action='store_true',
            help='A flag to specify overwriting existing PREMIS records. ' +
            'Defaults to False.'
        )

        self.parser.add_argument(
            '--premis',
            default=False,
            action='store_true',
            help='Create premis records for files ending in .premis.xml.' +
            'Defaults to False.'
        )

        self.parser.add_argument(
            '--fits',
            default=False,
            action='store_true',
            help='Create premis records for files ending in .fits.xml.' +
            'Defaults to False.'
        )

        args = self.parser.parse_args()

        path = abspath(args.path)
        if args.root:
            root = abspath(args.root)
        else:
            root = args.root
        stagereader = build_stage_reader(path, root)
        file_suites = stagereader.file_suites_paths

        records = []

        for x in file_suites:
            if x.premis and not args.overwrite:
                continue
            if not args.fits and \
                    StageReader.re_trailing_fits.search(x.original):
                continue
            if not args.premis and \
                    StageReader.re_trailing_premis.search(x.original):
                continue

            record = build_record(join(stagereader.root_fullpath, x.original))
            path = join(stagereader.root_fullpath,
                        stagereader.hypothesize_premis_from_orig_node(
                            stagereader.fpt.tree.get_node(x.original)
                        )
                        )
            tup = (record, path)
            records.append(tup)
            if args.batch_size:
                if len(records) >= args.batch_size:
                    write_records(records)
        write_records(records)
