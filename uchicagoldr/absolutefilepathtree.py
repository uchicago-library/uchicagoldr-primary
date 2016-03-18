from hashlib import sha256, md5
from os.path import isabs, isfile, isdir, exists, split, getsize
from collections import namedtuple
from mimetypes import guess_type
from magic import from_file

from uchicagoldr.filepathtree import FilePathTree
from uchicagoldr.convenience import sane_hash

class AbsoluteFilePathTree(FilePathTree):
    def __init__(self, path=None, filter_pattern=None, leaf_dirs=False):
        if path is not None:
            if not isabs(path):
                raise ValueError()

        FilePathTree.__init__(self, path=path, filter_pattern=filter_pattern, leaf_dirs=leaf_dirs)
        self.cache = namedtuple('Cache', ['shas', 'md5s', 'ext_mimes', 'magic_mimes', 'file_sizes', 'total_size'])


    def add_node(self, path):
        if not isabs(path):
            raise ValueError()
        FilePathTree.add_node(self, path)

    def get_files(self):
        return [x.identifier for x in self.get_leaf_nodes() if isfile(x.identifier)]

    def get_dirs(self):
        return [x.identifier for x in self.get_nodes() if isdir(x.identifier)]

    def get_leaf_dirs(self):
        return [x.identifier for x in self.get_leaf_nodes() if isdir(x.identifier)]

    def find_contents_of_a_subdirectory(self, path, recursive=False, all_files=[], inc_dirs=False):
        path_node = self.search_node_identifiers(path)[0]
        if inc_dirs:
            return [x.identifier for x in self.find_nodes_in_node(path_node, recursive=recursive)]
        return [x.identifier for x in self.find_nodes_in_node(path_node, recursive=recursive) if isfile(x.identifier)]

    def is_dir_in_tree(self, dirname):
        matches = self.search_node_tags(dirname)
        matches = [x for x in matches if isdir(x.identifier)]
        return matches

    def is_file_in_tree(self, filename):
        matches = self.search_node_tags(filename)
        matches = [x for x in matches if isfile(x.identifier)]
        return matches

    def is_file_in_subdirectory(self, dirname, filename):
        matches = []
        dir_matches = self.is_dir_in_tree(dirname)
        for x in dir_matches:
            for y in x.fpointer:
                if split(y)[1] == filename:
                   matches.append(y)
        return matches

    def find_shas(self):
        shas_dict = {}
        for x in self.get_files():
            shas_dict[x] = sane_hash('sha256', x)
        self.cache['shas'] = shas_dict

    def get_shas(self):
        if not self.cache['shas']:
            self.find_shas()
        return self.cache['shas']

    def find_md5s(self):
        md5s_dict = {}
        for x in self.get_files():
            md5s_dict[x] = sane_hash('md5', x)
        self.cache['md5s'] = md5s_dict

    def get_md5s(self):
        if not self.cache['md5s']:
            self.find_md5s()
        return self.cache['md5s']

    def find_mimes_from_extension(self):
        mimes_dict = {}
        for x in self.get_files():
            mimes_dict[x] = guess_type(x)[0]
        self.cache['ext_mimes'] = mimes_dict

    def get_mimes_from_extension(self):
        if not self.cache['ext_mimes']:
            self.find_mimes_from_extension()
        return self.cache['ext_mimes']

    def find_mimes_from_magic_number(self):
        mimes_dict = {}
        for x in self.get_files():
            mimes_dict[x] = from_file(x, mime=True).decode()
        self.cache['magic_mimes'] = mimes_dict

    def get_mimes_from_magic_number(self):
        if not self.cache['magic_mimes']:
            self.find_mimes_from_magic_number()
        return self.cache['magic_mimes']

    def find_file_sizes(self):
        size_dict = {}
        for x in self.get_files():
            size_dict[x] = getsize(x)
        self.cache['file_sizes'] = size_dict

    def get_file_sizes(self):
        if not self.cache['file_sizes']:
            self.find_file_sizes()
        return self.cache['file_sizes']

    def find_total_size(self):
        if not self.cache['file_sizes']:
            self.find_file_sizes()
        tote = 0
        for x in self.get_file_sizes():
            tote = tote + self.get_file_sizes()[x]
        self.cache['total_size'] = tote

    def get_total_size(self):
        if not self.cache['total_size']:
            self.find_total_size()
        return self.cache['total_size']
