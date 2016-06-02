from os import makedirs
from os.path import join, dirname, isfile
from uuid import uuid1
import mimetypes

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite.core.lib.bash_cmd import BashCommand
from .abc.converter import Converter
from ..structures.presformmaterialsuite import PresformMaterialSuite
from ..ldritems.ldritemoperations import copy
from ..ldritems.ldrpath import LDRPath
from ..processors.genericpremiscreator import GenericPREMISCreator


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class AudioConverter(Converter):
    """
    A class for converting a variety of audio files to FLAC
    """

    # Set the libreoffice path we'll be using in the bash command wrapper
    ffmpeg_path = 'ffmpeg'

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
        copy(self.source_materialsuite.premis, LDRPath(initd_premis_file))
        orig_premis = PremisRecord(frompath=initd_premis_file)
        orig_name = orig_premis.get_object_list()[0].get_originalName()
        # LibreOffice CLI won't let us just specify an output file name, so make
        # a while directory *just for it*.
        # ...
        # It also needs the input filename to be intact, I think, better safe
        # than sorry anyways.

        # Where we are putting our original file
        target_containing_dir = join(self.working_dir, str(uuid1()))
        target_path = join(target_containing_dir, orig_name)
        makedirs(dirname(target_path), exist_ok=True)
        copy(self.source_materialsuite.content, LDRPath(target_path))

        # Where we are aiming the LibreOffice CLI converter
        outdir = join(self.working_dir, str(uuid1()))
        makedirs(outdir)
        conv_file_path = join(outdir, orig_name+".presform.flac")

        # Fire 'er up
        convert_cmd_args = [self.ffmpeg_path, '-n', '-i', target_path,
                            conv_file_path]

        convert_cmd = BashCommand(convert_cmd_args)
        convert_cmd.set_timeout(self.timeout)
        convert_cmd.run_command()

        try:
            where_it_is = conv_file_path
            assert(isfile(where_it_is))
            presform_ldrpath = LDRPath(where_it_is)
            conv_file_premis = GenericPREMISCreator.instantiate_and_make_premis(
                presform_ldrpath,
                working_dir_path=self.working_dir
            )
            conv_file_premis_rec = PremisRecord(
                frompath=str(conv_file_premis.path)
            )
        except Exception:
            presform_ldrpath = None
            conv_file_premis_rec = None

        # Write a billion things into the PREMIS file(s)
        # This function handles None in the third arg sensibly, just updating
        # the original PREMIS file we have to specify a failed conversion
        self.handle_premis(convert_cmd.get_data(),
                           orig_premis,
                           conv_file_premis_rec,
                           "ffmpeg CLI FLAC Converter")

        # Update the original PREMIS regardless
        updated_premis_outpath = join(self.working_dir, str(uuid1()))
        orig_premis.write_to_file(updated_premis_outpath)
        self.get_source_materialsuite().set_premis(
            LDRPath(updated_premis_outpath)
        )

        # If the conversion was successful construct our PresformMaterialSuite
        # and add it to our source MaterialSuite
        if presform_ldrpath and conv_file_premis_rec:
            presform_ms = PresformMaterialSuite()
            presform_ms.set_extension(".flac")
            presform_ms.content = presform_ldrpath
            presform_premis_path = join(self.working_dir, str(uuid1()))
            conv_file_premis_rec.write_to_file(presform_premis_path)
            presform_ms.premis = LDRPath(presform_premis_path)
            self.source_materialsuite.add_presform(presform_ms)
