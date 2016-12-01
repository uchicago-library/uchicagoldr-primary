from json import dumps
from os.path import join, isfile
from uuid import uuid4
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.bash_cmd import BashCommand
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from .abc.converter import Converter

__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class VideoConverter(Converter):
    """
    A class for converting a variety of video file types to AVI
    """

    # Explicitly claimed mimes this converter should be able to handle
    _claimed_mimes = [
        "video/quicktime",
        'video/3gpp',
        'video/mp2p',
        'video/mp4',
        'video/mpeg',
        'video/mpv',
        'video/x-flv',
        'video/x-m4v',
        'video/x-ms-asf',
        'video/x-msvideo'
    ]

    # Try to look these extensions up in the python mimetypes class
    _claimed_extensions = [
        ".wmv",
        ".vob"
    ]

    @log_aware(log)
    def __init__(self, input_materialsuite, working_dir,
                 timeout=None, data_transfer_obj={}):
        """
        Instantiate a converter

        __Args__

        1. input_materialsuite (MaterialSuite): The MaterialSuite we want to
            try and make a presform for
        2. working_dir (str): A path the converter can work in without
            worrying about clobbering anything

        __KWArgs__

        * timeout (int): A timeout (in seconds) to kill the conversion process
            after.
        """
        log_init_attempt(self, log, locals())
        super().__init__(input_materialsuite,
                         working_dir=working_dir, timeout=timeout)
        self.converter_name = "ffmpeg video converter"
        self.ffmpeg_path = data_transfer_obj.get('ffmpeg_path', None)
        if self.ffmpeg_path is None:
            raise ValueError('No ffmpeg_path specified in the data' +
                             'transfer object!')
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attrib_dict = {
            'source_materialsuite': str(self.source_materialsuite),
            'working_dir': self.working_dir,
            'timeout': self.timeout,
            'claimed_mimes': self.claimed_mimes
        }

        return "<VideoConverter {}>".format(dumps(attrib_dict, sort_keys=True))

    @log_aware(log)
    def run_converter(self, in_path):
        """
        Edit the source materialsuite in place, adding any new presform
        materialsuites that we manage to make and updating its PREMIS record
        accordingly
        """
        conv_file_path = join(self.working_dir, uuid4().hex + ".flac")

        convert_cmd_args = [self.ffmpeg_path, '-n', '-i', in_path,
                            '-vcodec', 'rawvideo', '-acodec', 'pcm_u24le',
                            '-pix_fmt', 'uyvy422', '-vtag', '2vuy',
                            conv_file_path]

        convert_cmd = BashCommand(convert_cmd_args)
        convert_cmd.set_timeout(self.timeout)
        log.debug("Trying to convert to flac")
        convert_cmd.run_command()

        try:
            where_it_is = conv_file_path
            assert(isfile(where_it_is))
        except Exception:
            where_it_is = None
        return {'outpath': where_it_is, 'cmd_output': convert_cmd.get_data()}
