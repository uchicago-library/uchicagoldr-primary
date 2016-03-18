from uchicagoldr.filepathtree import FilePathTree

from os.path import isabs


class AbsoluteFilePathTree(FilePathTree):
    def __init__(self, path=None, filter_pattern=None, leaf_dirs=False):
        if path is not None:
            if not isabs(path):
                raise ValueError()

        FilePathTree.__init__(self, path=path, filter_pattern=filter_pattern, leaf_dirs=leaf_dirs)
        self.cache = namedtupe('Cache', ['shas', 'md5s', 'ext_mimes', 'magic_mimes', 'file_sizes', 'total_size'])

    def add_node(self, path):
        if not isabs(path):
            raise ValueError()
        FilePathTree.add_node(self, path)

    def get_files(self):
        pass

    def get_dirs(self):
        pass

    def get_leaf_dirs(self):
        pass

    def find_contents_of_a_subdirectory(self, n, recursive=False, all_files=[], inc_dirs=False):
        pass

    def is_it_a_subdirectory(self, n):
        pass

    def is_file_in_subdirectory(self, n, file_id):
        pass

    def find_shas(self):
        pass

    def get_shas(self):
        pass

    def find_md5s(self):
        pass

    def get_md5s(self):
        pass

    def find_mimes_from_extension(self):
        pass

    def get_mimes_from_extension(self):
        pass

    def find_mimes_from_magic_number(self):
        pass

    def get_mimes_from_magic_number(self):
        pass

    def find_file_sizes(self):
        pass

    def get_file_sizes(self):
        pass

    def find_total_size(self):
        pass

    def get_total_size(self):
        pass
