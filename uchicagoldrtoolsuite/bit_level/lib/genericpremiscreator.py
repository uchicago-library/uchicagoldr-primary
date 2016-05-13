from tempfile import TemporaryDirectory
from os.path import getsize, split
from mimetypes import guess_type
from uuid import uuid1
from os.path import join

from pypremis.lib import PremisRecord
from pypremis.nodes import *
try:
    from magic import from_file
except:
    pass

from ...core.lib.convenience import sane_hash
from .abc.ldritem import LDRItem
from .ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class GenericPREMISCreator(object):
    """
    Ingests a stage structure and produces a PREMIS stub object
    record for everything in it
    """
    def __init__(self, stage):
        """
        spawn a premis creator that should work for any LDRItems

        __Args__

        1. stage (Stage): The Stage to generate PREMIS object records for
        """
        self.stage = stage
        # This instance var should hold the dir open until the instance is
        # deleted from whatever script spawned it. Aka move this stuff
        # somewhere before your instance gets garbage collected.
        self.working_dir = TemporaryDirectory()
        self.working_dir_path = self.working_dir.name

    def process(self, skip_existing=False):
        """
        make the premis records for everything

        __KWArgs__

        * skip_existing (bool): If True: Skip all materialsuites which claim
            to already have PREMIS records as a part of them.
        """
        for segment in self.stage.segment_list:
            for materialsuite in segment.materialsuite_list:
                if skip_existing:
                    if isinstance(materialsuite.get_premis(), LDRItem):
                        continue
                materialsuite.set_premis(
                    self.instantiate_and_make_premis(materialsuite.content)
                )

    def instantiate_and_make_premis(self, item):
        """
        Write an item to a tempdir, examine it and make a PREMIS record

        __KWArgs__

        * item (LDRItem): The LDRItem to create a premis record for

        __Returns__

        * (LDRPath): The item representing the PREMIS record
        """
        recv_file = join(self.working_dir_path, str(uuid1()))
        premis_file = join(self.working_dir_path, str(uuid1()))
        with item.open('rb') as src:
            with open(recv_file, 'wb') as dst:
                dst.write(src.read(1024))
        rec = self.make_record(recv_file, item)
        rec.write_to_file(premis_file)
        return LDRPath(premis_file)

    def make_record(self, file_path, item):
        """
        build a PremisNode.Object from a file and use it to instantiate a record

        __Args__

        1. file_path (str): The full path to a file
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (PremisRecord): The populated record instance
        """
        obj = self._make_object(file_path, item)
        return PremisRecord(objects=[obj])

    def _make_object(self, file_path, item):
        """
        make an object entry auto-populated with the required information

        __Args__

        1. file_path (str): The path to the file
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (PremisRecord.Object): The populated Object... object
        """
        objectIdentifier = self._make_objectIdentifier()
        objectCategory = 'file'
        objectCharacteristics = self._make_objectCharacteristics(file_path, item)
        originalName = item.item_name
        storage = self._make_Storage(file_path)
        obj = Object(objectIdentifier, objectCategory, objectCharacteristics)
        obj.set_originalName(originalName)
        obj.set_storage(storage)
        return obj

    def _make_objectIdentifier(self):
        """
        mint a new object identifier

        __Returns__

        1. (PremisNode.ObjectIdentifier): A populated ObjectIdentifier
        """
        # uses uuid1 to generate DOIs. uuid1 should keep us unique by
        # hardware mac and time down to whatever accuracy time.time() has
        # plus some entropy. There's really fancy sounding posts on stack
        # overflow about why this should be fine
        return ObjectIdentifier("DOI", str(uuid1()))

    def _make_objectCharacteristics(self, file_path, item):
        """
        make a new objectCharacteristics node for a file

        __Args__

        1. file_path (str): The path to a file to generate info for
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (PremisNode.ObjectCharacteristics): a populated ObjectCharacteristics
        node
        """
        fixity1, fixity2 = self._make_fixity(file_path)
        size = str(getsize(file_path))
        formats = self._make_format(file_path, item)
        objChar = ObjectCharacteristics(formats[0])
        if len(formats) > 1:
            for x in formats[1:]:
                objChar.add_format(x)
        objChar.set_fixity(fixity1)
        objChar.add_fixity(fixity2)
        objChar.set_size(size)
        return objChar

    def _make_Storage(self, file_path):
        """
        make a new storage node for a file

        __Args__

        1. file_path (str): the path to a file to generate info for

        __Returns__

        1. (PremisNode.Storage): a populated storage node
        """
        contentLocation = self._make_contentLocation(file_path)
        stor = Storage()
        stor.set_contentLocation(contentLocation)
        return stor

    def _make_fixity(self, file_path):
        """
        make a fixity node for md5 and one for sha256 for a file

        __Args__

        1. file_path (str): The path to a file to generate info for

        __Returns__

        1. (PremisNode.Fixity): The md5 fixity node
        2. (PremisNode.Fixity): the sha256 fixity node
        """
        md5_fixity = Fixity('md5', sane_hash('md5', file_path))
        md5_fixity.set_messageDigestOriginator('python3 hashlib.md5')
        sha256_fixity = Fixity('sha256', sane_hash('sha256', file_path))
        sha256_fixity.set_messageDigestOriginator('python3 hashlib.sha256')
        return md5_fixity, sha256_fixity

    def _make_format(self, file_path, item):
        """
        make new format nodes for a file

        __Args__

        1. file_path (str): The path to the file to generate info for
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (list): a list of format nodes
        """
        magic_num, guess = self._detect_mime(file_path, item)
        formats = []
        if magic_num:
            premis_magic_format_desig = FormatDesignation(magic_num)
            premis_magic_format = Format(
                formatDesignation=premis_magic_format_desig
            )
            premis_magic_format.set_formatNote(
                'from magic number (python3 magic.from_file)'
            )
            formats.append(premis_magic_format)
        if guess:
            premis_guess_format_desig = FormatDesignation(guess)
            premis_guess_format = Format(
                formatDesignation=premis_guess_format_desig
            )
            premis_guess_format.set_formatNote(
                'from file extension (python3 mimetypes.guess_type)'
            )
            formats.append(premis_guess_format)
        if len(formats) == 0:
            premis_unknown_format_desig = FormatDesignation('undetected')
            premis_unknown_format = Format(
                formatDesignation=premis_unknown_format_desig
            )
            premis_unknown_format.set_formatNote(
                'format detection failed by python3 magic.from_file ' +
                'and mimetypes.guess_type'
            )
            formats.append(premis_unknown_format)
        return formats

    def _make_contentLocation(self, file_path):
        """
        make a new contentLocation node for a file

        __Args__

        1. file_path (str): The path to a file

        __Returns__

        1. (PremisNode): The populated contentLocation node
        """
        return ContentLocation("Unix File Path", file_path)

    def _detect_mime(self, file_path, item):
        """
        use both magic number and file extension mime detection on a file

        __Args__

        1. file_path (str): The path to the file in question
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (str): magic number mime detected
        2. (str): file extension mime detected
        """
        try:
            magic_num = from_file(file_path, mime=True).decode()
        except:
            magic_num = None
        try:
            guess = guess_type(item.item_name)[0]
        except:
            guess = None
        return magic_num, guess
