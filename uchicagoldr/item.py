from collections import namedtuple
from hashlib import md5, sha256
from magic import from_file
from os import access, stat, R_OK, walk, mkdir, rmdir, chown
from pwd import getpwnam
from grp import getgrnam
from os.path import exists, join, relpath, splitext, basename, isabs, abspath, \
    dirname, isdir
from mimetypes import guess_type
from re import compile as re_compile
from shutil import move
from re import match

from uchicagoldr.error import LDRNonFatal, LDRFatal
from uchicagoldr.output import Output
from uchicagoldr.request import ProvideNewFilePath, ProvideReadability, \
    ProvideNewRoot, ProvideNewArk, ProvideFileSize, ProvideMD5, \
    ProvideSHA256, ProvideFileExtension, ProvideMimetype, \
    ProvideCanonicalFilePath, ProvideDestinationDirectory, ProvideUserName, \
    ProvideGroupName


class Item(object):
    """
    This class holds the data for each regular file in a new batch
    """

    def __init__(self, path):
        assert(isabs(path))
        self.filepath = path
        self.set_readability(self.find_readability())

    def __repr__(self):
        return self.get_file_path()

    def __eq__(self, other):
        eq = type(self) == type(other) and self.get_file_path() == \
            other.get_file_path()
        return eq

    def _output_self_true(self):
        output = Output('item', status=True)
        if not output.add_data(self):
            raise ValueError
        return output

    def _output_self_false(self, requests=[], errors=[]):
        output = Output('item', status=False)
        for r in requests:
            output.add_request(r)
        for e in errors:
            output.add_error(e)
        if not output.add_data(self):
            raise ValueError
        return output

    def output(self):
        return self._output_self_true()

    def find_readability(self):
        if access(self.filepath, R_OK):
            return True
        else:
            return False

    def set_readability(self, readable_notice):
        try:
            if not isinstance(readable_notice, bool):
                fte = LDRFatal("The readability value can not be set to a "
                               "non-boolean value.")
                r = ProvideReadability(fte)
                return self._output_self_false(requests=[r])
            self.can_read = readable_notice
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def read_file(self):
        assert(self.can_read)
        with open(self.filepath, 'r') as f:
            fileData = f.read()
        return fileData

    def read_file_binary(self):
        assert(self.can_read)
        with open(self.filepath, 'rb') as f:
            fileData = f.read()
        return fileData

    def find_md5_hash(self):
        return self.find_hash_of_file(md5)

    def find_sha256_hash(self):
        return self.find_hash_of_file(sha256)

    def find_hash_of_file(self, hash_type, blocksize=65536):
        assert(self.can_read)

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
        afile.close()
        return hash.hexdigest()

    def set_md5(self, hash_value):
        try:
            if not isinstance(hash_value, str):
                fte = LDRFatal("The provided value for set md5 is " +
                               "not a string.")
                r = ProvideMD5(fte)
                return self._output_self_false(requests=[r])
            if not match("^[a-zA-Z\d]{32}$", hash_value):
                fte = LDRFatal("The provided string is not a valid " +
                               "md5 hash hex digest.")
                r = ProvideMD5(fte)
                return self._output_self_false(requests=[r])
            self.md5 = hash_value
            return self._output_self_true()
        except Exception as e:
            print(e)
            return self._output_self_false(errors=[LDRFatal(e)])

    def set_sha256(self, hash_value):
        try:
            if not isinstance(hash_value, str):
                fte = LDRFatal("The provided value for set sha256 is " +
                               "not a string.")
                r = ProvideSHA256(fte)
                return self._output_self_false(requests=[r])
            if not match("^[a-zA-Z\d]{64}$", hash_value):
                fte = LDRFatal("The provided string is not a valid " +
                               "sha256 hash hex digest.")
                r = ProvideSHA256(fte)
                return self._output_self_false(requests=[r])
            self.sha256 = hash_value
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def get_md5(self):
        return self.md5

    def get_sha256(self):
        return self.sha256

    def get_file_path(self):
        return self.filepath

    def set_file_path(self, new_file_path):
        try:
            if not isabs(new_file_path):
                fte = LDRFatal("The item filepath must be an absolute path.")
                r = ProvideNewFilePath(fte)
                return self._output_self_false(requests=[r])
            else:
                self.filepath = abspath(new_file_path)
                return self._output_self_true()
        except Exception as e:
            err = LDRFatal(e)
            return self._output_self_false(errors=[err])

    def find_file_name(self):
        return basename(self.filepath)

    def find_file_name_no_extension(self):
        return splitext(self.find_file_name())[0]

    def find_file_extension(self):
        return splitext(self.find_file_name())[1]

    def set_file_extension(self, value):
        try:
            if not isinstance(value, str):
                fte = LDRFatal("Argument passed to set file extension " +
                               "was not a string")
                r = ProvideFileExtension(fte)
                return self._output_self_false(requests=[r])
            if not match(".*\..*", value):
                fte = LDRFatal("Invalid file extension specified.")
                r = ProvideFileExtension(fte)
                return self._output_self_false(requests=[r])
            self.file_extension = value
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def get_file_extension(self):
        return self.file_extension

    def find_file_size(self):
        return stat(self.filepath).st_size

    def set_file_size(self, size_info):
        try:
            if not isinstance(size_info, int):
                fte = LDRNonFatal(
                    "The file size must be specified as an integer.")
                r = ProvideFileSize(fte)
                return self._output_self_false(requests=[r])
            self.file_size = size_info
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def get_file_size(self):
        return self.file_size

    def find_file_mime_type_from_extension(self):
        try:
            return guess_type(self.filepath)[0]
        except Exception as e:
            return (False, e)

    def find_file_mime_type_from_magic_number(self):
        try:
            return from_file(self.filepath, mime=True).decode("UTF-8")
        except Exception as e:
            return (False, e)

    def find_file_mime_type(self):
        try:
            mimetype = self.find_file_mime_type_from_extension()
            if mimetype is None:
                mimetype = self.find_file_mime_type_from_magic_number()
        except Exception:
            try:
                mimetype = self.find_file_mime_type_from_magic_number()
            except Exception:
                pass
        return mimetype

    def set_file_mime_type(self, mimetype_value):
        try:
            if not isinstance(mimetype_value, str):
                fte = LDRFatal("An invalid mimetype was specified.")
                r = ProvideMimetype(fte)
                return self._output_self_false(requests=[r])
            self.mimetype = mimetype_value
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def get_file_mime_type(self):
        return self.mimetype

    def find_technical_metadata(self):
        fits_filepath = self.get_file_path()+'.fits.xml'
        stif_filepath = self.get_file_path()+'.stif.txt'
        if exists(fits_filepath) or exists(stif_filepath):
            self.has_technical_md = True
            return True
        else:
            return False

    def find_matching_object_pattern(self, regex_pattern):
        assert isinstance(regex_pattern, type(re_compile("foo")))
        assert self.canonical_filepath
        matchable = regex_pattern.search(self.canonical_filepath)
        if matchable:
            return namedtuple("object_pattern", "status data")(True, matchable)
        else:
            return namedtuple("object_pattern", "status data")(False, None)


class AccessionItem(Item):

    def __init__(self, path, root, accession=None):
        Item.__init__(self, path)
        assert(isabs(root))
        self.root_path = abspath(root)
        if accession is None:
            self.set_accession(self.find_file_accession())

    def __eq__(self, other):
        return Item.__eq__(self, other) and self.get_root_path() == \
            other.get_root_path() and self.get_accession() == \
            other.get_accession()

    def _output_self_true(self):
        output = Output('accessionitem', status=True)
        if not output.add_data(self):
            raise ValueError
        return output

    def _output_self_false(self, requests=[], errors=[]):
        output = Output('accessionitem', status=False)
        for r in requests:
            output.add_request(r)
        for e in errors:
            output.add_error(e)
        if not output.add_data(self):
            raise ValueError
        return output

    def get_root_path(self):
        return self.root_path

    def set_root_path(self, new_root_path):
        try:
            if not isinstance(new_root_path, str):
                fte = LDRFatal("The root path specified was not a string.")
                r = ProvideNewRoot(fte)
                return self._output_self_false(requests=[r])
            if not isabs(new_root_path):
                fte = LDRNonFatal("The root path specified was not absolute.")
                r = ProvideNewRoot(fte)
                return self._output_self_false(requests=[r])
            self.root_path = abspath(new_root_path)
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def find_canonical_filepath(self):
        assert self.accession
        assert(self.get_root_path() in self.get_file_path() and
               self.get_accession() in self.get_file_path())
        return relpath(self.filepath, join(self.root_path, self.accession))

    def set_canonical_filepath(self, canonical_path):
        try:
            if not isinstance(canonical_path, str):
                fte = LDRFatal("The specified canonical path was invalid.")
                r = ProvideCanonicalFilePath(fte)
                return self._output_self_false(requests=[r])
            self.canonical_filepath = canonical_path
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def get_canonical_filepath(self):
        return self.canonical_filepath

    def find_file_accession(self):
        relative_path = relpath(self.filepath, self.root_path)
        accession, *tail = relative_path.split('/')
        return accession

    def set_accession(self, identifier):
        try:
            if not isinstance(identifier, str):
                fte = LDRFatal("The ARK specified was not a string.")
                r = ProvideNewArk(fte)
                return self._output_self_false(requests=[r])
            if not re_compile('^\w{13}$').match(identifier):
                fte = LDRNonFatal("The ARK specified was invalid.")
                r = ProvideNewArk(fte)
                return self._output_self_false(requests=[r])
            self.accession = identifier
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def get_accession(self):
        return self.accession

    def get_destination_path(self, new_root_directory):
        path_sans_root = relpath(self.filepath, self.root_path)
        destination_full_path = join(new_root_directory, path_sans_root)
        self.destination = destination_full_path
        return True

    def set_destination_path(self, new_root_directory):
        try:
            if not isabs(new_root_directory):
                fte = LDRFatal("The provided destination path is not " +
                               "absolute")
                r = ProvideDestinationDirectory(fte)
                return self._output_self_false(requests=[r])
            if not exists(new_root_directory):
                fte = LDRFatal("The provided destination path does not " +
                               "exist.")
                r = ProvideDestinationDirectory(fte)
                return self._output_self_false(requests=[r])
            if not isdir(new_root_directory):
                fte = LDRFatal("The provided destination path is not " +
                               "a directory.")
                r = ProvideDestinationDirectory(fte)
                return self._output_self_false(requests=[r])
            path_sans_root = relpath(self.filepath, self.root_path)
            destination_full_path = join(new_root_directory, path_sans_root)
            self.destination = destination_full_path
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def move_into_new_location(self):
        try:
            move(self.filepath, self.destination)
            return self._output_self_true()
        except Exception as e:
            error = LDRFatal(e)
            return self._output_self_false(errors=[error])

    def copy_source_directory_tree_to_destination(self):
        try:
            destination_directories = dirname(self.destination).split('/')
            directory_tree = ""
            for f in destination_directories:
                directory_tree = join(directory_tree, f)
                if not exists(directory_tree):
                    try:
                        mkdir(directory_tree, 0o740)
                    except Exception as e:
                        error = LDRFatal(e)
                        return self._output_self_false(errors=[error])
            return self._output_self_true()
        except Exception as e:
            return self._output_self_false(errors=[LDRFatal(e)])

    def clean_out_source_directory_tree(self):
        directory_tree = dirname(self.filepath)
        for src_dir, dirs, files in walk(directory_tree):
            try:
                rmdir(src_dir)
                return self._output_self_true()
            except Exception as e:
                error = LDRFatal(e)
                return self._output_self_false(errors=[error])

    def set_destination_ownership(self, user_name, group_name):
        try:
            if not isinstance(user_name, str):
                fte = LDRFatal("The specified user name was invalid.")
                r = ProvideUserName(fte)
                return self._output_self_false(requests=[r])
            if not isinstance(group_name, str):
                fte = LDRFatal("The specified group name was invalid.")
                r = ProvideGroupName(fte)
                return self.output_self_false(requests=[r])
            uid = getpwnam(user_name).pw_uid
            gid = getgrnam(group_name).gr_gid
            chown(self.destination, uid, gid)
            return self._output_self_true()
        except Exception as e:
            error = LDRFatal(e)
            return self._output_self_false(errors=[error])
