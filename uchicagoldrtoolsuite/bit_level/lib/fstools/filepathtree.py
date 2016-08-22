from os.path import join, split, isabs
from re import compile as re_compile

from treelib import Tree

from uchicagoldrtoolsuite.core.lib.masterlog import spawn_logger
from .filewalker import FileWalker
from .rootedpath import RootedPath


__author__ = "Brian Balsamo, Tyler Danstrom"
__email__ = "balsamo@uchicago.edu, tdanstrom@uchicago.edu"
__company__ = "The University of Chicago Library"
__copyright__ = "Copyright University of Chicago, 2016"
__publication__ = ""
__version__ = "0.0.1dev"


log = spawn_logger(__name__)


class FilePathTree(object):
    """
    A class meant to facilitate interacting with the contents of a file
    system as a tree diagram.

    __Attributes__

    1. tree (treelib.Tree): The underlying raw tree
    """
    def __init__(self, path=None, filter_pattern=None, leaf_dirs=False):
        """
        spawn a new instance of a FilePathTree

        __KWArgs__

        * path (str): an abspath to walk grabbing files to add to the tree
        structure
        * filter_pattern (str): If included, a regex filepaths must match
        in order to be included in the tree
        * leaf_dirs (bool): Whether or not to include directories with no
        contents in the tree
        """
        log.debug(
            "Spawning FilePathTree. " +
            "Path = {}. filter_pattern = {}. leaf_dirs = {}".format(
                str(path), filter_pattern, str(leaf_dirs)
            )
        )
        self.tree = Tree()
        if filter_pattern is not None:
            self.filter_pattern = re_compile(filter_pattern)
        else:
            self.filter_pattern = None
        if path:
            if not (isinstance(path, str) or isinstance(path, RootedPath)):
                raise ValueError()
            if isinstance(path, str):
                if not isabs(path):
                    raise ValueError()
            fw = FileWalker(path,
                            filter_pattern=filter_pattern,
                            inc_dirs=leaf_dirs)
            for i, path in enumerate(fw):
                if self.filter_pattern is not None:
                    if self.filter_pattern.match(i):
                        continue
                self.add_node(path)

    def __repr__(self):
        return str(self.tree.show())

    def __iter__(self):
        """
        yield all identifiers for nodes in the tree
        """
        for x in self.tree.all_nodes():
            yield x.identifier

    def _init_tree(self, path):
        """
        Initialize the tree root. For relpaths this will be "", for abspaths
        this will be "/"

        __Args__

        1. path (str): The path to init a tree for
        """
        if path[0] == '/':
            self.tree.create_node("/", "/")
        else:
            self.tree.create_node("", "")

    def add_node(self, path):
        """
        Add a full path to the tree structure, recursive

        __Args__

        1. path (str): The path representing the node(s) to be added

        """
        # Warning: this blows up if the tree was init'd with a relpath and you
        # try to add an abspath, or vice versa.
        if self.tree.root is None:
            self._init_tree(path)
        path_split = split(path)
        parent_path = path_split[0]
        leaf = path_split[1]
        if self.tree.get_node(path):
            return
        if not self.tree.get_node(parent_path):
            self.add_node(parent_path)
        self.tree.create_node(leaf, join(parent_path, leaf), parent=parent_path)

    def get_paths(self):
        """
        return all the paths for nodes in the tree

        __Returns__

        * (list): a list of paths for files and dirs in the tree
        """
        return [x.identifier for x in self.get_nodes()]

    def get_nodes(self):
        """
        Returns a list of the treelib.Node objects in the tree

        __Returns__

        * (list): A list of treelib.Nodes
        """
        return self.tree.all_nodes()

    def get_names(self):
        """
        Returns a list of EVERY filename/dirname in the tree

        __Returns__

        * (list): a list of filenames/dirnames in the tree
        """
        return [x.tag for x in self.get_nodes()]

    def get_leaf_nodes(self):
        """
        Get a list of all the leaves in the tree diagram

        __Returns__

        * (list): A list of all the leaves (treelib.Nodes) in the tree
        """
        return self.tree.leaves()

    def get_leaf_paths(self):
        """
        Get a list of all the leaf paths in the tree

        __Returns__

        * (list): A list of all the leaf paths (strs) in the tree
        """
        return [x.identifier for x in self.get_leaf_nodes()]

    def get_leaf_names(self):
        """
        Get a list of all the leaf names in the tree

        __Returns__

        * (list): A list of all the leaf names (strs) in the tree
        """
        return [x.tag for x in self.get_leaves()]

    def find_depth_of_a_node(self, node):
        """
        find the depth of a given node

        __Args__

        1. node (treelib.Node): The node to compute the depth of

        __Returns__

        * (int): The depth of the node
        """
        return self.tree.depth(node)

    def find_depth_of_a_path(self, path):
        """
        find the depth of a node with the given path

        __Args__

        1. path (str): the path of the node

        __Returns__

        * (int): The depth of the node with that path
        """
        for x in self.tree.all_nodes():
            if x.identifier == path:
                return self.find_depth_of_a_node(x)
        return None

    def trace_ancestry_of_a_node(self, node):
        """
        get a list of nodes from root to [node]

        __Args__

        1. node (treelib.Node): The node to get the ancestry of

        __Returns__

        * output (list): Each node in the given nodes ancestry, from root to
        itself
        """
        ancestry = [node]
        cur_node = node
        while self.tree.parent(cur_node.identifier):
            ancestry.append(self.tree.parent(cur_node.identifier))
            cur_node = self.tree.parent(cur_node.identifier)
        output = [n for n in reversed(ancestry)]
        return output

    def search_node_tags(self, q):
        """
        search a node for a tag

        __Args__

        q (str): the tag to search for

        __Returns__

        * (list): the list of nodes with that tag (almost assuredly just 1)
        """
        return [x for x in self.get_nodes() if q == x.tag]

    def search_node_identifiers(self, q):
        """
        search a node for an identifier

        __Args__

        q (str): the identifier to search for

        __Returns__

        * (list): the list of nodes with that identifier (should be just 1)
        """
        return [x for x in self.get_nodes() if q == x.identifier]

    def is_node_in_node(self, n, containing_n):
        """
        determine if one node is an immediate child of another

        __Args__

        1. n (treelib.Node): The node to search for
        2. containing_n (treelib.Node): The node to search

        __Returns__
        * (bool) whether or not n is in containing_n
        """
        if n.identifier in containing_n.fpointer:
            return True
        return False

    def does_node_match_string(self, n, id_string):
        """
        determine if a nodes id matches a given string

        __Args__

        1. n (treelib.Node): the node to match against
        2. id_string (str): the string to match against

        __Returns__

        * (bool): Whether or not they match
        """
        return n.identifier == id_string

    def find_string_in_node_tag(self, n, a_string):
        """
        determine if a string is in a nodes tag

        __Args__

        1. n (treelib.Node): the node
        2. a_string (str): the string to search for in the tag

        __Returns__
        * (bool): Whether or not that string is in the nodes tag
        """
        return a_string in n.tag

    def find_string_in_node_identifier(self, n, a_string):
        """
        determine if a string is in a nodes identifier

        __Args__

        1. n (treelib.Node): the node
        2. a_string (str): the string to search for in the identifier

        __Returns__
        * (bool): Whether or not that string is in the nodes identifier
        """
        return a_string in n.identifier

    def find_nodes_in_node(self, n, all_nodes=[], recursive=False):
        """
        Find all the nodes which are children of the specified node

        __Args__

        1. n (treelib.Node): The node to begin the search at

        __KWArgs__
        * all_nodes (list): primarily used for recursion, can seed the returned
        array
        * recursive (bool): Whether or not to recurse through children,
        grandchildren, etc

        __Returns__

        * all_nodes (list): A list of all the treelib.Nodes detected under
        n, either recursive or not as governed by the KWArgs
        """
        all_nodes = all_nodes + n.fpointer
        if recursive:
            for x in n.fpointer:
                if not x.is_leaf():
                    self.find_nodes_in_node(x, all_nodes=all_nodes,
                                            recursive=recursive)
        return all_nodes

    def find_leaves_in_node(self, n, all_leaves=[], recursive=False):
        """
        find all the leaf nodes which are children of the specified node

        __Args__

        1. n (treelib.Node): the node to begin the search at

        __KWArgs__

        * all_leaves (list): primarily used for recursion, can seed the results
        * recursive (bool): whether or not to scan children, grandchildren,
        etc for leaves
        """
        all_leaves = all_leaves + [x for x in n.fpointer if x.is_leaf()]
        if recursive:
            for x in n.fpointer:
                if not x.is_leaf():
                    self.find_leaves_in_node(x, all_leaves=all_leaves,
                                             recursive=recursive)
        return all_leaves

    def find_tag_at_depth(self, tag, depth):
        """
        find all nodes at a given depth with a given tag

        __Args__

        1. tag (str): the tag to look for
        2. depth (int): the depth to look at

        __Returns__

        * matches (list): A list of treelib.Nodes which have the specified
        tag and are at the specified depth
        """
        potential_matches = [x for x in self.search_node_tags(tag)]
        matches = [x for x in potential_matches if
                   self.find_depth_of_a_node(x) == depth]
        return matches
