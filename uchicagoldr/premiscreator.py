from os.path import split, getsize, isdir, join
from os import makedirs
from hashlib import md5, sha256
from magic import from_file
from mimetypes import guess_type
from uuid import uuid1
from uchicagoldr.rootedpath import RootedPath
from uchicagoldr.stagereader import StageReader
from pypremis.lib import PremisRecord
from pypremis.nodes import *

"""
A class for automatically building PREMIS object records for items in a staging
directory.

__Attribs__

* data_root (str): The path to the data directory of the staging dir
* admin_root (str): The path to the admin directory of the staging dir
* premis_records (list): a list of tuples populated by build_records(). The
tuples are (PremisRecord instance, proposed write path)
"""

class PremisCreator(object):
    def __init__(self, directory, root=None, overwrite=False):
        stage_path = RootedPath(directory, root=root)
        self.stagereader = StageReader(stage_path)

    def build_records(self, overwrite=False, not_for_fits=True, not_for_premis=True):
        """
        populate the self.premis_records array with tuples containing
        a premis record instance and a proposed filepath for writing to.
        """
        record_tuples = []
        for x in self.stagereader.file_suites_paths:
            if x.premis and not overwrite:
                continue
            if not_for_fits and StageReader.re_trailing_fits.search(x.original):
                continue
            if not_for_premis and StageReader.re_trailing_premis.search(x.original):
                continue

            rel_file_path = x.original
            rel_record_file_path = self.stagereader.hypothesize_premis_from_orig_node(self.stagereader.fpt.tree.get_node(x.original))
            full_file_path = join(self.stagereader.root_fullpath, rel_file_path)
            record_file_path = join(self.stagereader.root_fullpath, rel_record_file_path)
            record = self.make_record(full_file_path)
            record_tuples.append((record, record_file_path))
        self.premis_records = record_tuples

    def write_records(self):
        """
        iterate through the premis_records array writing to designated paths
        """
        for x in self.premis_records:
            self.write_record_to_disk(x[0], x[1])

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

    def determine_record_location(self, file_path):
        """
        assume a file is in a valid staging dir, determine where its record
        should go.

        __Args__

        1. file_path (str): The full path to a file

        __Returns__

        1. (str): The proposed file path to write to
        """

    def write_record_to_disk(self, record, file_path):
        """
        write a premis record to disk at a location, creating necessary dirs

        __Args__

        1. record (PremisRecord): The PremisRecord instance to be written
        2. file_path (str): Where to write the file.
        """
        if not isdir (split(file_path)[0]):
            makedirs(split(file_path)[0])
        record.write_to_file(file_path)

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

    def _sane_hash(self, hasher, file_path, block_size=65536):
        """
        hash a file with the given hasher

        __Args__

        1. hasher (hashlib func): The hashing function to use
        2. file_path (str): The path to the file to be hashed

        __KWArgs__

        * block_size (int): The maximum number of bytes to be read into
        memory in one go

        __Returns__

        1. (str): The hash hex digest
        """
        hash_result = hasher()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data:
                    break
                hash_result.update(data)
        return str(hash_result.hexdigest())

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
        md5_fixity = Fixity('md5', self._sane_hash(md5, file_path))
        md5_fixity.set_messageDigestOriginator('python3 hashlib.md5')
        sha256_fixity = Fixity('sha256', self._sane_hash(sha256, file_path))
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
        magic_num, guess  = self._detect_mime(file_path)
        formats = []
        if magic_num:
            premis_magic_format_desig = FormatDesignation(magic_num)
            premis_magic_format = Format(formatDesignation=premis_magic_format_desig)
            premis_magic_format.set_formatNote('from magic number (python3 magic.from_file)')
            formats.append(premis_magic_format)
        if guess:
            premis_guess_format_desig = FormatDesignation(guess)
            premis_guess_format = Format(formatDesignation=premis_guess_format_desig)
            premis_guess_format.set_formatNote('from file extension (python3 mimetypes.guess_type)')
            formats.append(premis_guess_format)
        if len(formats) == 0:
            premis_unknown_format_desig = FormatDesignation('undetected')
            premis_unknown_format = Format(formatDesignation=premis_unknown_format_desig)
            premis_unknown_format.set_formatNote('format detection failed by python3 magic.from_file and mimetypes.guess_type')
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
