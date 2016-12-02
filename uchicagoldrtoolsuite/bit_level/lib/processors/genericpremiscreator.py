from tempfile import TemporaryDirectory
from os import fsdecode
from os.path import getsize
from mimetypes import guess_type
from json import dumps
from logging import getLogger

try:
    from magic import from_file
except:
    pass
from pypremis.lib import PremisRecord
from pypremis.nodes import *

from uchicagoldrtoolsuite import log_aware
from uchicagoldrtoolsuite.core.lib.convenience import sane_hash
from uchicagoldrtoolsuite.core.lib.convenience import log_init_attempt, \
    log_init_success
from uchicagoldrtoolsuite.core.lib.idbuilder import IDBuilder
from ..ldritems.ldritemcopier import LDRItemCopier
from ..ldritems.abc.ldritem import LDRItem
from ..ldritems.ldrpath import LDRPath


__author__ = "Brian Balsamo"
__email__ = "balsamo@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = getLogger(__name__)


class GenericPREMISCreator(object):
    """
    Ingests a stage structure and produces a PREMIS stub object
    record for everything in it

    This class itself is kind of a loose wrapper around the real workhorse
    class methods, which are employed fairly often themselves in other
    processors at the MaterialSuite level
    """
    @log_aware(log)
    def __init__(self, stage):
        """
        spawn a premis creator that should work for any LDRItems

        __Args__

        1. stage (Stage): The Stage to generate PREMIS object records for
        """
        log_init_attempt(self, log, locals())
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
        log_init_success(self, log)

    @log_aware(log)
    def __repr__(self):
        attr_dict = {
            'stage': str(self.stage),
            'working_dir_path': self.working_dir_path
        }
        return "<GenericPREMISCreator {}>".format(
            dumps(attr_dict, sort_keys=True))

    @log_aware(log)
    def process(self, skip_existing=False, set_originalName=True):
        """
        make the premis records for everything

        __KWArgs__

        * skip_existing (bool): If True: Skip all materialsuites which claim
            to already have PREMIS records as a part of them.
        """
        log.debug("Beginning PREMIS processing")
        ms_num = 0
        ms_tot = len(self.stage.materialsuite_list)
        for materialsuite in self.stage.materialsuite_list:
            ms_num += 1
            log.debug(
                "Processing MaterialSuite {}/{}".format(
                    str(ms_num),
                    str(ms_tot)
                )
            )
            if skip_existing:
                if isinstance(materialsuite.get_premis(), LDRItem):
                    log.debug("PREMIS detected: Skipping")
                    continue
            log.debug("No PREMIS detected: Creating")
            materialsuite.set_premis(
                self.instantiate_and_make_premis(
                    materialsuite.content,
                    self.working_dir_path,
                    set_originalName=set_originalName
                )
            )

    @classmethod
    @log_aware(log)
    def process_materialsuite(cls, materialsuite, originalName=None):
        """
        Ingests a MaterialSuite and sets its PREMIS data

        __Args__

        1. materialsuite (MaterialSuite): The MaterialSuite to produce the
            PREMIS data for

        __KWArgs__

        * originalName (str): The originalName to set in the PREMIS record
        """
        log.debug(
            "Processing MaterialSuite, supplied originalName: {}".format(
                str(originalName)
            )
        )

        log.debug("Establishing temporary file locations")
        tmp_file_path = TemporaryFilePath()
        new_premis_path = TemporaryFilePath()
        try:
            tmp_files = getattr(materialsuite, tmp_files)
            tmp_files.append(new_premis_path)
        except:
            materialsuite.tmp_files = [new_premis_path]
        tmp_ldritem = LDRPath(tmp_file_path.path)
        log.debug("Instantiating content")
        c = LDRItemCopier(materialsuite.content, tmp_ldritem)
        cr = c.copy()
        assert(cr['src_eqs_dst'] is True)
        log.debug("Creating PREMIS")
        premis = make_record(tmp_file_path.path, original_name=originalName)
        log.debug("Writing created PREMIS to tmp file.")
        premis.write_to_file(new_premis_path.path)
        materialsuite.premis = LDRPath(new_premis_path.path)

    @classmethod
    @log_aware(log)
    def make_record(cls, file_path, original_name=None):
        """
        build a PremisNode.Object from a file and use it to instantiate a record

        __Args__

        1. file_path (str): The full path to a file
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (PremisRecord): The populated record instance
        """
        log.debug("Generating PREMIS from supplied file path")
        obj = cls._make_object(file_path, original_name)
        rec = PremisRecord(objects=[obj])
        log.debug("PremisRecord generated")
        return rec

    @classmethod
    @log_aware(log)
    def _make_object(cls, file_path, original_name=None):
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
        objectCharacteristics = cls._make_objectCharacteristics(file_path, original_name)
        storage = cls._make_Storage(file_path)
        obj = Object(objectIdentifier, objectCategory, objectCharacteristics)
        if original_name is not None:
            obj.set_originalName(original_name)
        obj.set_storage(storage)
        return obj

    @classmethod
    @log_aware(log)
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
    @log_aware(log)
    def _make_objectCharacteristics(cls, file_path, original_name):
        """
        make a new objectCharacteristics node for a file

        __Args__

        1. file_path (str): The path to a file to generate info for
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (PremisNode.ObjectCharacteristics): a populated ObjectCharacteristics
        node
        """
        fixitys = cls._make_fixity(file_path)
        size = str(getsize(file_path))
        formats = cls._make_format(file_path, original_name)
        objChar = ObjectCharacteristics(formats[0])
        if len(formats) > 1:
            for x in formats[1:]:
                objChar.add_format(x)
        for x in fixitys:
            if x is not None:
                objChar.add_fixity(x)
        objChar.set_size(size)
        return objChar

    @classmethod
    @log_aware(log)
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
    @log_aware(log)
    def _make_fixity(cls, file_path):
        """
        make a fixity node for md5 and one for sha256 for a file

        __Args__

        1. file_path (str): The path to a file to generate info for

        __Returns__

        1. fixitys ([PremisNode.Fixity]): fixity nodes including computed
            values
        """
        fixitys = []
        with open(file_path, 'rb') as f:
            try:
                md5_fixity = Fixity('md5', sane_hash('md5', f))
                md5_fixity.set_messageDigestOriginator('python3 hashlib.md5')
                fixitys.append(md5_fixity)
            except:
                pass
        with open(file_path, 'rb') as f:
            try:
                sha256_fixity = Fixity('sha256', sane_hash('sha256', f))
                sha256_fixity.set_messageDigestOriginator('python3 hashlib.sha256')
                fixitys.append(sha256_fixity)
            except:
                pass
        with open(file_path, 'rb') as f:
            try:
                crc32_fixity = Fixity('crc32', sane_hash('crc32', f))
                crc32_fixity.set_messageDigestOriginator('python3 zlib.crc32')
                fixitys.append(crc32_fixity)
            except:
                pass
        with open(file_path, 'rb') as f:
            try:
                adler32_fixity = Fixity('adler32', sane_hash('adler32', f))
                adler32_fixity.set_messageDigestOriginator('python3 zlib.adler32')
                fixitys.append(adler32_fixity)
            except:
                pass
        return fixitys

    @classmethod
    @log_aware(log)
    def _make_format(cls, file_path, original_name):
        """
        make new format nodes for a file

        __Args__

        1. file_path (str): The path to the file to generate info for
        2. item (LDRItem): The LDRItem representative of the file contents

        __Returns__

        1. (list): a list of format nodes
        """
        magic_num, guess = cls._detect_mime(file_path, original_name)
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
    @log_aware(log)
    def _make_contentLocation(cls, file_path):
        """
        make a new contentLocation node for a file

        __Args__

        1. file_path (str): The path to a file

        __Returns__

        1. (PremisNode): The populated contentLocation node
        """
        return ContentLocation("Unix File Path", fsdecode(file_path))

    @classmethod
    @log_aware(log)
    def _detect_mime(cls, file_path, original_name):
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
            magic_num = from_file(file_path, mime=True)
        except:
            magic_num = None
        try:
            guess = guess_type(original_name)[0]
        except:
            guess = None
        return magic_num, guess
