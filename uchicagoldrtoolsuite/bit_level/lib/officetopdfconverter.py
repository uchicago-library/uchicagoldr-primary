from os import listdir, makedirs
from os.path import join, dirname, isfile
from uuid import uuid1
import mimetypes

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from ...core.lib.bash_cmd import BashCommand
from ...core.lib.convenience import iso8601_dt
from .abc.converter import Converter
from .presformmaterialsuite import PresformMaterialSuite
from .ldritemoperations import copy
from .ldrpath import LDRPath
from .genericpremiscreator import GenericPREMISCreator


class OfficeToPDFConverter(Converter):
    """
    A class for converting a variety of "office" file types to PDF-A

    ********************
    Note: Libreoffice doesn't currently have a CLI option for PDF-A.
    You have to flip it in the GUI and then the setting holds.
    ********************
    """

    # Set the libreoffice path we'll be using in the bash command wrapper
    libre_office_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

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

    # Add the stuff we want looked up to the _claimed_mimes array if it's in
    # the python mimetypes lib database. Otherwise pass.
    mimetypes.init()
    for x in _claimed_extensions:
        try:
            _claimed_mimes.append(mimetypes.types_map[x])
        except KeyError:
            pass

    # Get rid of any duplicates in our list
    _claimed_mimes = list(set(_claimed_mimes))

    def __init__(self, input_materialsuite, working_dir,
                 timeout=None):
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

    def convert(self):
        """
        Edit the source materialsuite in place, adding any new presform
        materialsuites that we manage to make and updating its PREMIS record
        accordingly
        """
        initd_premis_file = join(self.working_dir, str(uuid1()))
        outdir = join(self.working_dir, str(uuid1()))
        makedirs(outdir)
        copy(self.source_materialsuite.premis, LDRPath(initd_premis_file))
        orig_premis = PremisRecord(frompath=initd_premis_file)
        orig_name = orig_premis.get_object_list()[0].get_originalName()
        # LibreOffice CLI won't let us just specify an output file name, so make
        # a while directory *just for it*.
        # ...
        # It also needs the input filename to be intact, I think, better safe
        # than sorry anyways.
        target_containing_dir = join(self.working_dir, str(uuid1()))
        target_path = join(target_containing_dir, orig_name)
        makedirs(dirname(target_path), exist_ok=True)
        copy(self.source_materialsuite.content, LDRPath(target_path))

        convert_cmd_args = [self.libre_office_path, '--headless',
                            '--convert-to', 'pdf', '--outdir', outdir,
                            target_path]
        convert_cmd = BashCommand(convert_cmd_args)
        convert_cmd.set_timeout(self.timeout)
        convert_cmd.run_command()
        # If there's anything in the outdir we gave libreoffice thats what we
        # want, if there isn't the conversion failed for some reason
        try:
            where_it_is = join(outdir, listdir(outdir)[0])
            assert(isfile(where_it_is))
        except:
            where_it_is = None

        # Alright, we now know whether or not the conversion succeeded. Update
        # the events in the originals PREMIS file.

        if where_it_is is not None:
            presform_ldrpath = LDRPath(where_it_is)
            conv_file_premis = GenericPREMISCreator.instantiate_and_make_premis(
                presform_ldrpath,
                working_dir_path=self.working_dir,
            )
            conv_file_premis_rec = PremisRecord(frompath=str(conv_file_premis.path))
        else:
            conv_file_premis_rec = None

        self.handle_premis(convert_cmd.get_data(), orig_premis, conv_file_premis_rec,
                            "LibreOffice CLI PDF Converter")

        updated_premis_outpath = join(self.working_dir, str(uuid1()))
        orig_premis.write_to_file(updated_premis_outpath)
        self.get_source_materialsuite().set_premis(LDRPath(updated_premis_outpath))

        if where_it_is:
            presform_ms = PresformMaterialSuite()
            presform_ms.set_extension(".pdf")
            presform_ms.content = presform_ldrpath
            presform_premis_path = join(self.working_dir, str(uuid1()))
            conv_file_premis_rec.write_to_file(presform_premis_path)
            presform_ms.premis = LDRPath(presform_premis_path)
            self.source_materialsuite.add_presform(presform_ms)
