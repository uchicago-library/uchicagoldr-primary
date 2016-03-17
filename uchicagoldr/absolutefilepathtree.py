from uchicagoldr.filepathtree import FilePathTree

from os.path import isabs


class AbsoluteFilePathTree(FilePathTree):
    def __init__(self, path=None, filter_pattern=None, leaf_dirs=False):
        if path is not None:
            if not isabs(path):
                raise ValueError()

        FilePathTree.__init__(self, path=path, filter_pattern=filter_pattern, leaf_dirs=leaf_dirs)

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
