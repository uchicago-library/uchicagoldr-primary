from uuid import uuid1

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.filesystemstagereader import FileSystemStageReader
from ..lib.archivestructure import ArchiveStructure
from ..lib.filesystemarchivestructurewriter import FileSystemArchiverStructureWriter


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
                          "for moving materials into staging structures.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("directory", type=str, action='store')
        self.parser.add_argument("source_root", type=str, action='store')
        self.parser.add_argument("destination_root", type=str, action='store')

        # Parse arguments into args namespace
        args = self.parser.parse_args()
        staging_reader = StagingDirectoryReader(args.directory)
        archive_structure = ArchiveStructure(uuid1())
        staging_structure = staging_reader.read()
        archivable_premisrecords = []
        archivable_dataobjects = []
        archivable_techmdrecords = []
        archivable_accessionrecords = []
        for n_segment in staging_structure.segment:
            for n_msuite in n_segment.materialsuite:
                archivable_premisrecords.extend(n_msuite.premis)
                archivable_techmdrecords.extend(n_msuite.technicalmetadata)
                archivable_dataobjects.extend(n_msuite.original)
                archivable_dataobjects.extend(n_msuite.presform)

        for n_record in staging_structure.accessionrecord:
            archivable_accessionrecords.extend(n_record)
        archive_structure.accession_record = archivable_accessionrecords
        archive_structure.premis_object = archivable_premisrecords
        archive_structure.data_object = archivable_dataobjects
        archive_structure.technical_metadata = archivable_techmdrecords

        archiver_writer = FileSystemArchiverStructureWriter(archive_structure)
        archiver_writer.write()

if __name__ == "__main__":
    a = Archiver()
    a.main()
