from os.path import isdir, abspath, split, join
from os import makedirs
from xml.etree.ElementTree import register_namespace

from pypremis.lib import PremisRecord

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
#from uchicagoldrtoolsuite.lib.stagereader import StageReader
from ..lib.technicalmetadatarecordcreator \
    import TechnicalMetadataRecordCreator
from .premisobjectcreator import build_stage_reader


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


def launch():
    """
    the hook for setuptools console scripts
    """
    app = TechnicalMetadataRecordUtility(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


def build_record(path, premisfp, timeout):
    """
    build a new FITS record. Update the corresponding PREMIS record
    in place

    __Args__

    1) path (str): the path to the file to be examined
    2) premisfp (str): The path to the files PREMIS object record
    3) timeout (int): How long to give FITS with the files before aborting

    __Returns__

    record (xml.etree.ElementTree): The FITS record
    """
    premis = PremisRecord(frompath=premisfp)
    builder = TechnicalMetadataRecordCreator(path, premis, timeout=timeout)
    record = builder.get_record()
    premis = builder.get_premis()
    # dump all the ns0 prints
    register_namespace('', 'http://hul.harvard.edu/ois/xml/ns/fits/fits_output')
    premis.write_to_file(premisfp)
    return record


def write_records(records):
    """
    write a stack of record tuples to their specified locations

    __Args__

    1) records (list): A list of tuples in the format (FITS Record instance,
    proposed path)
    """
    while records:
        x = records.pop()
        target_path = x[1]
        record = x[0]
        if not isdir(split(target_path)[0]):
            makedirs(split(target_path)[0])
        record.write(target_path)


class TechnicalMetadataCreator(CLIApp):
    """
    The CLI App for generating FITS records for staged materials
    """
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for creating original technical metadata records " +
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
        self.parser.add_argument(
            '--timeout',
            default=43200,
            type=int,
            help='Specify how many seconds can elapse while a single ' +
            'fits record is being produced. Default is 12 hours'
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
            if x.fits and not args.overwrite:
                continue
#            if not args.fits and \
#                    StageReader.re_trailing_fits.search(x.original):
                continue
#            if not args.premis and \
#                    StageReader.re_trailing_premis.search(x.original):
                continue

            record = build_record(join(stagereader.root_fullpath, x.original),
                                  join(stagereader.root_fullpath, x.premis[0]),
                                  args.timeout)
            path = join(stagereader.root_fullpath,
                        stagereader.hypothesize_fits_from_orig_node(
                            stagereader.fpt.tree.get_node(x.original)
                        )
                        )
            tup = (record, path)
            records.append(tup)
            if args.batch_size:
                if len(records) >= args.batch_size:
                    write_records(records)
        write_records(records)
