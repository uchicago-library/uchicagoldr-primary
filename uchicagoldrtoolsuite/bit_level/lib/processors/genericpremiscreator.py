from tempfile import TemporaryDirectory
from os.path import getsize
from mimetypes import guess_type
from uuid import uuid1
from os.path import join
from json import dumps

from pypremis.lib import PremisRecord
from pypremis.nodes import *
try:
    from magic import from_file
except:
    pass

from uchicagoldrtoolsuite.core.lib.convenience import sane_hash
from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder
from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from uchicagoldrtoolsuite.core.lib.exceptionhandler import ExceptionHandler
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.abc.ldritem import LDRItem
from ..ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"

log = spawn_logger(__name__)
eh = ExceptionHandler()

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
        log.debug(
            "GenericPREMISCreator created tmpdir @ {}".format(
            self.working_dir_path)
        )
        log.debug("GenericPREMISCreator spawned: {}".format(str(self)))

    def __repr__(self):
        attr_dict = {
            'stage': str(self.stage),
            'working_dir_path': self.working_dir_path
        }
        return "<GenericPREMISCreator {}>".format(dumps(attr_dict, sort_keys=True))

    def process(self, skip_existing=False):
        """
        make the premis records for everything

        __KWArgs__

        * skip_existing (bool): If True: Skip all materialsuites which claim
            to already have PREMIS records as a part of them.
        """
        log.debug("Beginning PREMIS processing")
        s_num = 0
        for segment in self.stage.segment_list:
            s_num += 1
            ms_num = 0
            for materialsuite in segment.materialsuite_list:
                ms_num += 1
                log.debug(
                    "Processing Section {}/{}, MaterialSuite {}/{}".format(
                        str(s_num),
                        str(len(self.stage.segment_list)),
                        str(ms_num),
                        str(len(segment.materialsuite_list))
                    )
                )
                if skip_existing:
                    if isinstance(materialsuite.get_premis(), LDRItem):
                        log.debug("PREMIS detected: Skipping")
                        continue
                try:
                    log.debug("No PREMIS detected: Creating")
                    materialsuite.set_premis(
                        self.instantiate_and_make_premis(materialsuite.content,
                                                        self.working_dir_path)
                    )
                except Exception as e:
                    eh.handle(e)

    @classmethod
    def instantiate_and_make_premis(cls, item, working_dir_path):
        """
        Write an item to a tempdir, examine it and make a PREMIS record

        __Args__

        1. item (LDRItem): The LDRItem to create a premis record for

        __KWArgs__

        * working_dir_path (str): Where to write things to disk. Defaults
            to the current instances working_dir_path

        __Returns__

        * (LDRPath): The item representing the PREMIS record
        """
        recv_file = join(working_dir_path, str(uuid1()))
        premis_file = join(working_dir_path, str(uuid1()))
        recv_item = LDRPath(recv_file)
        c = LDRItemCopier(item, recv_item, clobber=True)
        r = c.copy()
        rec = cls.make_record(recv_file, item)
        rec.write_to_file(premis_file)
        recv_item.delete(final=True)
        return LDRPath(premis_file)

    @classmethod
    def make_record(cls, file_path, item):
        """
        build a PremisNode.Object from a file and use it to instantiate a record

        __Args__

        1. file_path (str): The full path to a file
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (PremisRecord): The populated record instance
        """
        obj = cls._make_object(file_path, item)
        return PremisRecord(objects=[obj])

    @classmethod
    def _make_object(cls, file_path, item):
        """
        make an object entry auto-populated with the required information

        __Args__

        1. file_path (str): The path to the file
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (PremisRecord.Object): The populated Object... object
        """
        objectIdentifier = cls._make_objectIdentifier()
        objectCategory = 'file'
        objectCharacteristics = cls._make_objectCharacteristics(file_path, item)
        originalName = item.item_name
        storage = cls._make_Storage(file_path)
        obj = Object(objectIdentifier, objectCategory, objectCharacteristics)
        obj.set_originalName(originalName)
        obj.set_storage(storage)
        return obj

    @classmethod
    def _make_objectIdentifier(cls):
        """
        mint a new object identifier

        __Returns__

        1. (PremisNode.ObjectIdentifier): A populated ObjectIdentifier
        """
        # uses uuid1 to generate DOIs. uuid1 should keep us unique by
        # hardware mac and time down to whatever accuracy time.time() has
        # plus some entropy. There's really fancy sounding posts on stack
        # overflow about why this should be fine
        idb = IDBuilder()
        identifier_tup = idb.build('premisID').show()
        return ObjectIdentifier(identifier_tup[0], identifier_tup[1])

    @classmethod
    def _make_objectCharacteristics(cls, file_path, item):
        """
        make a new objectCharacteristics node for a file

        __Args__

        1. file_path (str): The path to a file to generate info for
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (PremisNode.ObjectCharacteristics): a populated ObjectCharacteristics
        node
        """
        fixity1, fixity2 = cls._make_fixity(file_path)
        size = str(getsize(file_path))
        formats = cls._make_format(file_path, item)
        objChar = ObjectCharacteristics(formats[0])
        if len(formats) > 1:
            for x in formats[1:]:
                objChar.add_format(x)
        objChar.set_fixity(fixity1)
        objChar.add_fixity(fixity2)
        objChar.set_size(size)
        return objChar

    @classmethod
    def _make_Storage(cls, file_path):
        """
        make a new storage node for a file

        __Args__

        1. file_path (str): the path to a file to generate info for

        __Returns__

        1. (PremisNode.Storage): a populated storage node
        """
        contentLocation = cls._make_contentLocation(file_path)
        stor = Storage()
        stor.set_contentLocation(contentLocation)
        return stor

    @classmethod
    def _make_fixity(cls, file_path):
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

    @classmethod
    def _make_format(cls, file_path, item):
        """
        make new format nodes for a file

        __Args__

        1. file_path (str): The path to the file to generate info for
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (list): a list of format nodes
        """
        magic_num, guess = cls._detect_mime(file_path, item)
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

    @classmethod
    def _make_contentLocation(cls, file_path):
        """
        make a new contentLocation node for a file

        __Args__

        1. file_path (str): The path to a file

        __Returns__

        1. (PremisNode): The populated contentLocation node
        """
        return ContentLocation("Unix File Path", file_path)

    @classmethod
    def _detect_mime(cls, file_path, item):
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
