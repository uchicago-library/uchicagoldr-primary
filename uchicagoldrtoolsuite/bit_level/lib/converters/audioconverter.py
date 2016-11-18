from os.path import join, isfile
from uuid import uuid4
from json import dumps
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.bash_cmd import BashCommand
from .abc.converter import Converter


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class AudioConverter(Converter):
    """
    A class for converting a variety of audio files to FLAC
    """

    # Explicitly claimed mimes this converter should be able to handle
    _claimed_mimes = [
        'audio/x-aiff',
        'audio/basic',
        'audio/midi',
        'audio/mp4',
        'audio/mpeg',
        'audio/x-ape',
        'audio/x-pn-realaudio',
        'audio/x-wav'
    ]

    # Try to look these extensions up in the python mimetypes class
    _claimed_extensions = [
        '.mp3',
        '.wma',
        '.wav',
        '.aiff',
        '.midi'
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

        * data_transfer_obj (dict): A dictionary carrying potential converter-
            specific configuration values.
        """
        super().__init__(input_materialsuite,
                         working_dir=working_dir, timeout=timeout)
        self.converter_name = "ffmpeg audio converter"
        self.ffmpeg_path = data_transfer_obj.get('ffmpeg_path', None)
        if self.ffmpeg_path is None:
            raise ValueError('No ffmpeg_path specified in the data ' +
                             'transfer object!')
        log.debug("AudioConverter spawned: {}".format(str(self)))

    @log_aware(log)
    def __repr__(self):
        attrib_dict = {
            'source_materialsuite': str(self.source_materialsuite),
            'working_dir': self.working_dir,
            'timeout': self.timeout,
            'claimed_mimes': self.claimed_mimes
        }

        return "<AudioConverter {}>".format(dumps(attrib_dict, sort_keys=True))

    @log_aware(log)
    def run_converter(self, in_path):
        """
        Runs ffmpeg against {in_path} in order to generate a flac file

        See the Converter ABC to see how this fits into the whole workflow

        __Args__

        in_path (str): The path where the original file is located

        __Returns__

        (dict): A dictionary used by the converter ABC
        """
        conv_file_path = join(self.working_dir, uuid4().hex + ".flac")
        # Fire 'er up
        convert_cmd_args = [self.ffmpeg_path, '-n', '-i', in_path,
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
