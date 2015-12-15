from collections import namedtuple
from hashlib import md5, sha256
from magic import from_file
from os import access, stat, R_OK
from os.path import exists, join, relpath, splitext, basename
from mimetypes import guess_type
from re import compile as re_compile


class Item(object):
    """
    This class holds the data for each regular file in a new batch
    """

    root_path = ""
    filepath = ""
    sha256 = ""
    md5 = ""
    accession = ""
    mimetype = ""
    index_hash = ""
    index_mimetype = ""
    index_size = ""
    canonical_filepath = ""
    can_read = False
    has_technical_md = False

    def __init__(self, path, root):
        self.root_path = root
        self.filepath = join(root, path)
        self.set_readability(self.test_readability())

    def test_readability(self):
        if access(self.filepath, R_OK):
            return True
        else:
            return False

    def get_root_path(self):
        return self.root_path

    def set_root_path(self, new_root_path):
        self.root_path = new_root_path

    def set_readability(self, readable_notice):
        self.can_read = readable_notice

    def read_file(self):
        with open(self.filepath, 'r') as f:
            fileData = f.read()
        return fileData

    def read_file_binary(self):
        with open(self.filepath, 'rb') as f:
            fileData = f.read()
        return fileData

    def find_md5_hash(self):
        return self.find_hash_of_file(md5)

    def find_sha256_hash(self):
        return self.find_hash_of_file(sha256)

    def find_hash_of_file(self, hash_type, blocksize=65536):
        def check():
            if hash_type.__name__ == sha256.__name__ or \
               hash_type.__name__ == md5.__name__:
                return True
            else:
                return False
        assert check()
        hash = hash_type()
        afile = open(self.filepath, 'rb')
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hash.update(buf)
            buf = afile.read(blocksize)
        return hash.hexdigest()

    def set_md5(self, hash_value):
        self.md5 = hash_value

    def set_sha256(self, hash_value):
        self.sha256 = hash_value

    def get_md5(self):
        return self.md5

    def get_sha256(self):
        return self.sha256

    def get_file_path(self):
        return self.filepath

    def set_file_path(self, new_file_path):
        self.file_path = new_file_path

    def find_canonical_filepath(self):
        assert self.accession
        return relpath(self.filepath, join(self.root_path, self.accession))

    def set_canonical_filepath(self, canonical_path):
        self.canonical_filepath = canonical_path

    def get_canonical_filepath(self):
        return self.canonical_filepath

    def find_file_accession(self):
        relative_path = relpath(self.filepath, self.root_path)
        accession, *tail = relative_path.split('/')
        return accession

    def set_accession(self, identifier):
        if re_compile('^\w{13}$').match(identifier):
            self.accession = identifier
        else:
            raise ValueError("You did not pass a valid noid")

    def find_file_name(self):
        return basename(self.filepath)

    def find_file_name_no_extension(self):
        return splitext(basename(self.filepath))[0]

    def get_accession(self):
        return self.accession

    def find_file_extension(self):
        filename = basename(self.filepath)
        return splitext(filename)[1]

    def set_file_extension(self, value):
        self.file_extension = value

    def get_file_extension(self):
        return self.file_extension

    def find_file_size(self):
        return stat(self.filepath).st_size

    def set_file_size(self, size_info):
        if isinstance(size_info, int):
            self.file_size = size_info
        else:
            raise ValueError("You did not pass an integer.")

    def get_file_size(self):
        return self.file_size

    def find_file_mime_type_from_extension(self):
        try:
            return guess_type(self.filepath)[0]
        except Exception as e:
            return (False, e)

    def find_file_mime_type_from_magic_numbers(self):
        try:
            return from_file(self.filepath, mime=True)
        except Exception as e:
            return (False, e)

    def find_file_mime_type(self):
        try:
            mimetype = self.find_file_mime_type_from_extension()
        except Exception:
            try:
                mimetype = self.find_file_mime_type_from_magic_number()
            except Exception:
                pass
        return mimetype

    def set_file_mime_type(self, mimetype_value):
        self.mimetype = mimetype_value

    def get_file_mime_type(self):
        return self.mimetype

    def find_technical_metadata(self):
        fits_filepath = self.filepath+'.fits.xml'
        stif_filepath = self.filepath+'.stif.txt'
        if exists(fits_filepath) or exists(stif_filepath):
            self.has_technical_md = True
        else:
            pass
        return True

    def get_destination_path(self, new_root_directory):
        path_sans_root = relpath(self.filepath, self.root_path)
        destination_full_path = join(new_root_directory, path_sans_root)
        self.destination = destination_full_path
        return True

    def set_destination_path(self, new_path):
        self.destination = new_path

    def find_matching_object_pattern(self, regex_pattern):
        assert isinstance(regex_pattern, type(re_compile("foo")))
        assert self.canonical_filepath
        matchable = regex_pattern.search(self.canonical_filepath)
        if matchable:
            return namedtuple("object_pattern", "status data")(True, matchable)
        else:
            return namedtuple("object_pattern", "status data")(False, None)
