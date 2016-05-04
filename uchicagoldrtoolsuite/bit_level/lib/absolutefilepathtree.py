from os.path import isabs, isfile, isdir, split, getsize
from mimetypes import guess_type

from .filepathtree import FilePathTree
from ...core.lib.convenience import sane_hash


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


class AbsoluteFilePathTree(FilePathTree):
    """
    A class meant to enforce that a FilePathTree contains only absolute paths
    that are located on addressable disk
    """
    def __init__(self, path=None, filter_pattern=None, leaf_dirs=False):
        """
        init a new instance of an AbsoluteFilePathTree, enforcing an abspath

        [see FilePathTree.__init__()]
        """
        if path is not None:
            if not isabs(path):
                raise ValueError()
        self.shas = None
        self.md5s = None
        self.ext_mimes = None
        self.magic_mimes = None
        self.file_sizes = None
        self.total_size = None

        FilePathTree.__init__(self, path=path, filter_pattern=filter_pattern,
                              leaf_dirs=leaf_dirs)

    def add_node(self, path):
        """
        Enforces paths are absolute

        [see FilePathTree.add_node()]
        """
        if not isabs(path):
            raise ValueError()
        FilePathTree.add_node(self, path)

    def get_files(self):
        """
        Return a list of each file in the tree

        __Returns__

        * (list): A list of fullpaths (strs) for each *file* in the tree
        """
        return [x.identifier for x in self.get_leaf_nodes() if
                isfile(x.identifier)]

    def get_dirs(self):
        """
        Return a list of each dir in the tree

        __Returns__

        * (list): a list of fullpaths (strs) for each *directory* in the tree
        """
        return [x.identifier for x in self.get_nodes() if isdir(x.identifier)]

    def get_leaf_dirs(self):
        """
        return a list of leaf directories in the tree

        __Returns__

        * (list): a list of fullpaths (strs) for each leaf dir
        """
        return [x.identifier for x in self.get_leaf_nodes() if
                isdir(x.identifier)]

    def find_contents_of_a_subdirectory(self, path, recursive=False,
                                        all_files=[], inc_dirs=False):
        """
        find the contents of a directory

        __Args__

        1. path (str): The abspath of the dir

        __KWArgs__

        * recursive (bool): whether or not to recurse into child dirs
        * all_files (list): primarily for recursion, can be used to seed
        results
        * inc_dirs (bool): whether or not to include directories in the return
        list

        __Returns__

        * (list): A list of fullpaths (strs) for the contents of a subdir
        """
        path_node = self.search_node_identifiers(path)[0]
        if inc_dirs:
            return [x.identifier for x in
                    self.find_nodes_in_node(path_node, recursive=recursive)]
        return [x.identifier for x in
                self.find_nodes_in_node(path_node, recursive=recursive) if
                isfile(x.identifier)]

    def is_dir_in_tree(self, dirname):
        """
        return dirs in tree with the given str in their name

        __Args__

        1. dirname (str): a full/partial dirname

        __Returns__

        * matches (list): dirs with the dirname in their tag in the tree
        """
        matches = self.search_node_tags(dirname)
        matches = [x for x in matches if isdir(x.identifier)]
        return matches

    def is_file_in_tree(self, filename):
        """
        return files in tree with the given str in their name

        __Args__

        1. filename (str): a full/partial filename

        __Returns__

        * matches (list): files with the filename in their tag in the tree
        """
        matches = self.search_node_tags(filename)
        matches = [x for x in matches if isfile(x.identifier)]
        return matches

    def is_file_in_subdirectory(self, dirname, filename):
        """
        check to see if a given partial filename appears in a partial dirname

        __Args__

        1. dirname (str): the dirname to look for
        2. filename (str): the filename to look for in those dirs

        __Returns__

        * matches (list): files with filename in their tag which are in dirs
        with dirname in their tag
        """
        matches = []
        dir_matches = self.is_dir_in_tree(dirname)
        for x in dir_matches:
            for y in x.fpointer:
                if split(y)[1] == filename:
                    matches.append(y)
        return matches

