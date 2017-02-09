from logging import getLogger
from os.path import join
from tempfile import TemporaryDirectory
from configparser import NoOptionError

from pypairtree.utils import identifier_to_path

from pypremis.lib import PremisRecord

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from ..lib.ldritems.ldrpath import LDRPath
from ..lib.ldritems.ldritemcopier import LDRItemCopier
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.readers.filesystemarchivereader import FileSystemArchiveReader
from ..lib.processors.genericpresformcreator import \
    GenericPresformCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


def launch():
    """
    entry point launch hook
    """
    app = PresformCreator(
            __author__=__author__,
            __email__=__email__,
            __company__=__company__,
            __copyright__=__copyright__,
            __publication__=__publication__,
            __version__=__version__
    )
    app.main()


class PresformCreator(CLIApp):
    """
    Creates PRESFORM files for the contents of a stage
    """
    @log_aware(log)
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for creating presforms for materials in " +
                          "a stage.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        log.debug("Adding application specific cli app arguments")
        self.parser.add_argument("target_archive_identifier",
                                 help="The identifier of the archive of " +
                                 "materials for which to generate presforms.",
                                 type=str)
        self.parser.add_argument("destination_stage_id", help="The id of a " +
                                 "stage to create in which to deposit the " +
                                 "the presforms",
                                 type=str, action='store')
        self.parser.add_argument("live_premis_root",
                                 help="The path to the root of your " +
                                 "live Premis directory.",
                                 type=str)
        self.parser.add_argument("--skip_existing", help="Skip material " +
                                 "suites which already claim to have " +
                                 "at least one presform",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable_office2pdf",
                                 help="Disable the OfficeToPDFConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable_office2csv",
                                 help="Disable the OfficeToCSVConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable_office2txt",
                                 help="Disable the OfficeToTXTConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable_videoconverter",
                                 help="Disable the VideoConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable_imageconverter",
                                 help="Disable the ImageConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable_audioconverter",
                                 help="Disable the AudioConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--staging_env", help="The path to your " +
                                 "staging environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--lts_env", help="The path to your " +
                                 "long term storage environment",
                                 type=str,
                                 default=None)
        self.parser.add_argument("--eq_detect", help="The equality " +
                                 "metric to use on writing, check " +
                                 "LDRItemCopier for supported schemes.",
                                 type=str, action='store',
                                 default="bytes")
        self.parser.add_argument("--ffmpeg_path",
                                 help="The path to the ffmpeg executable." +
                                 "This option will override the conf.",
                                 action='store',
                                 default=None)
        self.parser.add_argument("--libre_office_path",
                                 help="The path to the LibreOffice " +
                                 "executable." +
                                 "This option will override the conf.",
                                 action='store',
                                 default=None)

        # Parse arguments into args namespace
        args = self.parser.parse_args()
        self.process_universal_args(args)

        # App code

        dto = {}
        try:
            dto['ffmpeg_path'] = self.conf.get("Paths", 'ffmpeg_path')
        except NoOptionError:
            pass
        try:
            dto['libre_office_path'] = self.conf.get("Paths",
                                                     'libre_office_path')
        except NoOptionError:
            pass

        if args.ffmpeg_path is not None:
            dto['ffmpeg_path'] = args.ffmpeg_path
        if args.libre_office_path is not None:
            dto['libre_office_path'] = args.libre_office_path

        if args.staging_env:
            staging_env = args.staging_env
        else:
            staging_env = self.conf.get("Paths", "staging_environment_path")
        staging_env = self.expand_path(staging_env)

        if args.lts_env:
            lts_env = args.lts_env
        else:
            lts_env = self.conf.get("Paths", "long_term_storage_environment_path")
        lts_env = self.expand_path(lts_env)

        src_archive_reader = FileSystemArchiveReader(lts_env,
                                                     args.target_archive_identifier)

        dst_stage_reader = FileSystemStageReader(staging_env,
                                                 args.destination_stage_id)
        src_archive = src_archive_reader.read()
        dst_stage = dst_stage_reader.read()
        if not len(dst_stage.materialsuite_list) == 0:
            raise ValueError("Target stage isn't empty!")

        log.info("Target Archive: " + join(lts_env, str(identifier_to_path(args.target_archive_identifier))))
        log.info("Destination Stage: " + join(staging_env, args.destination_stage_id))

        log.info("Processing...")

        converters = []

        if not args.disable_office2pdf:
            from ..lib.converters.officetopdfconverter import \
                OfficeToPDFConverter
            converters.append(OfficeToPDFConverter)
        if not args.disable_office2csv:
            from ..lib.converters.officetocsvconverter import \
                OfficeToCSVConverter
            converters.append(OfficeToCSVConverter)
        if not args.disable_office2txt:
            from ..lib.converters.officetotxtconverter import \
                OfficeToTXTConverter
            converters.append(OfficeToTXTConverter)
        if not args.disable_videoconverter:
            from ..lib.converters.videoconverter import VideoConverter
            converters.append(VideoConverter)
        if not args.disable_imageconverter:
            from ..lib.converters.imageconverter import ImageConverter
            converters.append(ImageConverter)
        if not args.disable_audioconverter:
            from ..lib.converters.audioconverter import AudioConverter
            converters.append(AudioConverter)

        working_dir = TemporaryDirectory()
        for ms in src_archive.materialsuite_list:
            src_ms_id = ms.identifier
            src_livepremis_path = join(args.live_premis_root,
                                       str(identifier_to_path(args.target_archive_identifier)),
                                       "arf",
                                       "pairtree_root",
                                       str(identifier_to_path(src_ms_id)),
                                       "arf", "premis.xml")
            ms.premis = LDRPath(src_livepremis_path)
            premis = PremisRecord(frompath=src_livepremis_path)
            try:
                for relation in premis.get_object_list()[0].get_relationship():
                    if relation.get_relationshipType() == 'derivation' \
                            and relation.get_relationshipSubType() == 'is Source of':
                        has_presforms = True
                        break
            except KeyError:
                pass
            presforms = GenericPresformCreator.instantiate_and_make_presforms(
                ms,
                working_dir.name,
                converters,
                dto
            )
            for x in presforms:
                dst_stage.materialsuite_list.append(x)
            copier = LDRItemCopier(ms.premis, LDRPath(src_livepremis_path), clobber=True)
            copier.copy()



        log.info("Writing...")
        writer = FileSystemStageWriter(dst_stage, staging_env,
                                       eq_detect=args.eq_detect)
        writer.write()
        del working_dir
        log.info("Complete")


if __name__ == "__main__":
    s = PresformCreator()
    s.main()
