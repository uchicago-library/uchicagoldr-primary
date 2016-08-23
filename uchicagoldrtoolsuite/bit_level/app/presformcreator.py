from sys import stdout
from os.path import join
from configparser import NoOptionError

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
from uchicagoldrtoolsuite.core.lib.masterlog import \
    spawn_logger, \
    activate_master_log_file, \
    activate_job_log_file, \
    activate_stdout_log
from ..lib.writers.filesystemstagewriter import FileSystemStageWriter
from ..lib.readers.filesystemstagereader import FileSystemStageReader
from ..lib.processors.genericpresformcreator import \
    GenericPresformCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)
activate_master_log_file()
activate_job_log_file()


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
    def main(self):
        # Instantiate boilerplate parser
        self.spawn_parser(description="The UChicago LDR Tool Suite utility " +
                          "for creating presforms for materials in " +
                          "a stage.",
                          epilog="{}\n".format(self.__copyright__) +
                          "{}\n".format(self.__author__) +
                          "{}".format(self.__email__))
        # Add application specific flags/arguments
        self.parser.add_argument("stage_id", help="The id of the stage",
                                 type=str, action='store')
        self.parser.add_argument("--skip-existing", help="Skip material " +
                                 "suites which already claim to have " +
                                 "at least one presform",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable-office2pdf",
                                 help="Disable the OfficeToPDFConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable-office2csv",
                                 help="Disable the OfficeToCSVConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable-office2txt",
                                 help="Disable the OfficeToTXTConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable-videoconverter",
                                 help="Disable the VideoConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable-imageconverter",
                                 help="Disable the ImageConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--disable-audioconverter",
                                 help="Disable the AudioConverter",
                                 action='store_true',
                                 default=False)
        self.parser.add_argument("--staging_env", help="The path to your " +
                                 "staging environment",
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

        activate_stdout_log(args.verbosity)

        # Set conf
        self.set_conf(conf_dir=args.conf_dir, conf_filename=args.conf_file)

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

        stage_fullpath = join(staging_env, args.stage_id)
        reader = FileSystemStageReader(stage_fullpath)
        stage = reader.read()
        log.info("Stage: " + stage_fullpath)

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

        presform_creator = GenericPresformCreator(stage, converters)
        presform_creator.process(skip_existing=args.skip_existing,
                                 data_transfer_obj=dto)

        writer = FileSystemStageWriter(stage, staging_env, eq_detect=args.eq_detect)
        writer.write()
        log.info("Complete")


if __name__ == "__main__":
    s = PresformCreator()
    s.main()
