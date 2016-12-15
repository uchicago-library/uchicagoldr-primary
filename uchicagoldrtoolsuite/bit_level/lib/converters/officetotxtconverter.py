from os import scandir, makedirs
from json import dumps
from os.path import join, isfile
from uuid import uuid4
from logging import getLogger

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.bash_cmd import BashCommand
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from uchicagoldrtoolsuite.core.lib.apiagentmixin import APIAgentMixin
from .abc.converter import Converter


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class OfficeToTXTConverter(Converter, APIAgentMixin):
    """
    A class for converting a variety of "office" file types to TXT
    """

    # Explicitly claimed mimes this converter should be able to handle
    _claimed_mimes = [
        'application/rtf',
        'application/pdf',
        'application/msword',
        'application/vnd.ms-powerpoint',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    ]

    # Try to look these extensions up in the python mimetypes class
    _claimed_extensions = [
        '.doc',
        '.docx',
        '.odt',
        '.fodt',
        '.ppt',
        '.pptx',
        '.odp',
        '.fodp',
        '.odf',
        '.pdf',
        '.rtf'
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
        log_init_attempt(self, log, locals())
        super().__init__(input_materialsuite,
                         working_dir=working_dir, timeout=timeout)
        self.libre_office_path = data_transfer_obj.get(
            'libre_office_path', None
        )
        if self.libre_office_path is None:
            raise ValueError('No libre_office_path specificed in the data' +
                             'transfer object!')
        self.converter_name = self._construct_name()
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attrib_dict = {
            'source_materialsuite': str(self.source_materialsuite),
            'working_dir': self.working_dir,
            'timeout': self.timeout,
            'claimed_mimes': self.claimed_mimes
        }

        return "<OfficeToTXTConverter {}>".format(
            dumps(attrib_dict, sort_keys=True))

    @log_aware(log)
    def _construct_name(self):
        ver_com_args = [self.libre_office_path, '--version']
        ver_com = BashCommand(ver_com_args)
        ver_com.run_command()
        assert(ver_com.get_data()[0])
        return "Office to TXT Converter ({})".format(
            ver_com.get_data()[1].stdout.split("\n")[0]
        )

    @log_aware(log)
    def run_converter(self, in_path):
        """
        Runs libreoffice against {in_path} in order to generate a txt file

        See the Converter ABC to see how this fits into the whole workflow

        __Args__

        in_path (str): The path where the original file is located

        __Returns__

        (dict): A dictionary used by the converter ABC
        """
        # LibreOffice is a little crazy, and won't let us specify a complete
        # outpath for the file - just an outdir, so we make one just for it and
        # then assume that the only file in there is the result of the
        # conversion (which it should be)
        outdir = join(self.working_dir, uuid4().hex)
        makedirs(outdir, exist_ok=True)
        convert_cmd_args = [self.libre_office_path, '--headless',
                            '--convert-to', 'txt:Text', '--outdir', outdir,
                            in_path]
        convert_cmd = BashCommand(convert_cmd_args)
        convert_cmd.set_timeout(self.timeout)
        log.debug("Attempting conversion to txt")
        convert_cmd.run_command()
        try:
            log.debug("Conversion success, file located in the outdir")
            where_it_is = join(outdir, [x.name for x in scandir(outdir)][0])
            assert(isfile(where_it_is))
        except:
            log.debug("Conversion failure, no file in outdir")
            where_it_is = None

        return {'outpath': where_it_is, 'cmd_output': convert_cmd.get_data()}

    def get_premis_agent_record(self):
        return super().get_premis_agent_record(name=self.converter_name)
