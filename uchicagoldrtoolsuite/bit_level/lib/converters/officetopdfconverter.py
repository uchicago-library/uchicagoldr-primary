from os import scandir, makedirs
from json import dumps
from os.path import join, dirname, isfile
from uuid import uuid4
import mimetypes

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite.core.lib.bash_cmd import BashCommand
from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from .abc.converter import Converter
from ..structures.materialsuite import MaterialSuite
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.ldrpath import LDRPath
from ..processors.genericpremiscreator import GenericPREMISCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class OfficeToPDFConverter(Converter):
    """
    A class for converting a variety of "office" file types to PDF-A

    ********************
    Note: Libreoffice doesn't currently have a CLI option for PDF-A.
    You have to flip it in the GUI and then the setting holds.
    ********************
    """

    # Explicitly claimed mimes this converter should be able to handle
    _claimed_mimes = [
        'text/plain',
        'text/csv',
        'application/rtf',
        'application/pdf',
        'application/msword',
        'application/vnd.ms-powerpoint',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    # Try to look these extensions up in the python mimetypes class
    _claimed_extensions = [
        '.doc',
        '.docx',
        '.odt',
        '.fodt',
        '.xls',
        '.xlsx',
        '.ods',
        '.fods',
        '.ppt',
        '.pptx',
        '.odp',
        '.fodp',
        '.odf',
        '.odg',
        '.pdf',
        '.txt',
        '.rtf',
        '.csv'
    ]

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
        super().__init__(input_materialsuite,
                         working_dir=working_dir, timeout=timeout)
        self.converter_name = "LibreOffice PDF Converter"
        self.libre_office_path = data_transfer_obj.get('libre_office_path', None)
        if self.libre_office_path is None:
            raise ValueError('No libre_office_path specificed in the data' +
                             'transfer object!')
        log.debug("OfficeToPDFConverter spawned: {} ".format(str(self)))

    def __repr__(self):
        attrib_dict = {
            'source_materialsuite': str(self.source_materialsuite),
            'working_dir': self.working_dir,
            'timeout': self.timeout,
            'claimed_mimes': self.claimed_mimes
        }

        return "<OfficeToPDFConverter {}>".format(
            dumps(attrib_dict, sort_keys=True))

    def run_converter(self, in_path):
        outdir = join(self.working_dir, uuid4().hex)
        makedirs(outdir, exist_ok=True)
        convert_cmd_args = [self.libre_office_path, '--headless',
                            '--convert-to', 'pdf', '--outdir', outdir,
                            in_path]
        convert_cmd = BashCommand(convert_cmd_args)
        convert_cmd.set_timeout(self.timeout)
        convert_cmd.run_command()
        try:
            where_it_is = join(outdir, [x.name for x in scandir(outdir)][0])
            assert(isfile(where_it_is))
        except:
            where_it_is = None

        return {'outpath': where_it_is, 'cmd_output': convert_cmd.get_data()}
