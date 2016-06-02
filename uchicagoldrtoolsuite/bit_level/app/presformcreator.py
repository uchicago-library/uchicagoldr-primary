from sys import stdout
from os.path import join

from uchicagoldrtoolsuite.core.app.abc.cliapp import CLIApp
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

        # Parse arguments into args namespace
        args = self.parser.parse_args()

        # Set conf
        self.set_conf(conf_dir=args.conf_dir, conf_filename=args.conf_file)

        # App code

        if args.staging_env:
            staging_env = args.staging_env
        else:
            staging_env = self.conf.get("Paths", "staging_environment_path")

        # App code
        stage_fullpath = join(staging_env, args.stage_id)
        reader = FileSystemStageReader(stage_fullpath)
        stage = reader.read()
        stdout.write("Stage: " + stage_fullpath + "\n")

        stdout.write("Processing...\n")

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
        presform_creator.process(skip_existing=args.skip_existing)

        writer = FileSystemStageWriter(stage, staging_env)
        writer.write()
        stdout.write("Complete\n")


if __name__ == "__main__":
    s = PresformCreator()
    s.main()
