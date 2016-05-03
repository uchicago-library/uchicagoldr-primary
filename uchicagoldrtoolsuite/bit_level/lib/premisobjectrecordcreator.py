from os.path import getsize, split
from mimetypes import guess_type
from uuid import uuid1

from pypremis.lib import PremisRecord
from pypremis.nodes import *

from ...core.lib.convenience import sane_hash

try:
    from magic import from_file
except:
    pass


class PremisObjectRecordCreator(object):
    """
    This class is meant to automate the construction of standard minimal
    LDR object PREMIS records from some input file.

    __Attributes__

    1. file_path (str): The abspath to a file for which a record will be created
    2. record (PremisRecord): The associated PREMIS record instance, which
    will contain one object entry populated with the files information.
    """
    def __init__(self, path):
        """
        initialize an LDR PREMIS object record.

        __Args__

        1. path (str): the abspath to a file to create a record for
        """
        self.file_path = path
        self.record = self.make_record(self.file_path)

    def make_record(self, file_path):
        """
        build a PremisNode.Object from a file and use it to instantiate a record

        __Args__

        1. file_path (str): The full path to a file

        __Returns__

        1. (PremisRecord): The populated record instance
        """
        obj = self._make_object(file_path)
        return PremisRecord(objects=[obj])

    def get_record(self):
        return self.record

    def _make_object(self, file_path):
        """
        make an object entry auto-populated with the required information

        __Args__

        1. file_path (str): The path to the file

        __Returns__

        1. (PremisRecord.Object): The populated Object... object
        """
        objectIdentifier = self._make_objectIdentifier()
        objectCategory = 'file'
        objectCharacteristics = self._make_objectCharacteristics(file_path)
        originalName = split(file_path)[1]
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

    def _make_objectCharacteristics(self, file_path):
        """
        make a new objectCharacteristics node for a file

        __Args__

        1. file_path (str): The path to a file to generate info for

        __Returns__

        1. (PremisNode.ObjectCharacteristics): a populated ObjectCharacteristics
        node
        """
        fixity1, fixity2 = self._make_fixity(file_path)
        size = str(getsize(file_path))
        formats = self._make_format(file_path)
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

    def _make_format(self, file_path):
        """
        make new format nodes for a file

        __Args__

        1. file_path (str): The path to the file to generate info for

        __Returns__

        1. (list): a list of format nodes
        """
        magic_num, guess = self._detect_mime(file_path)
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

    def _detect_mime(self, file_path):
        """
        use both magic number and file extension mime detection on a file

        __Args__

        1. file_path (str): The path to the file in question

        __Returns__

        1. (str): magic number mime detected
        2. (str): file extension mime detected
        """
        try:
            magic_num = from_file(file_path, mime=True).decode()
        except:
            magic_num = None
        try:
            guess = guess_type(file_path)[0]
        except:
            guess = None
        return magic_num, guess
