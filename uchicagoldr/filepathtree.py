from os.path import join, split, isabs
from treelib import Tree
from uchicagoldr.filewalker import FileWalker
from uchicagoldr.rootedpath import RootedPath


class FilePathTree(object):
    def __init__(self, path=None, filter_pattern=None, leaf_dirs=False):
        self.tree = Tree()
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
                self.add_node(path)

    def __repr__(self):
        return str(self.tree.show())

    def __iter__(self):
        for x in self.tree.all_nodes():
            yield x.identifier

    def _init_tree(self, path):
        if path[0] == '/':
            self.tree.create_node("/", "/")
        else:
            self.tree.create_node("", "")

    def add_node(self, path):
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
        return [x.identifier for x in self.get_file_nodes()]

    def get_nodes(self):
        return self.tree.all_nodes()

    def get_names(self):
        return [x.tag for x in self.get_file_nodes()]

    def get_leaf_nodes(self):
        return self.tree.leaves()

    def get_leaf_paths(self):
        return [x.identifier for x in self.get_leaves()]

    def get_leaf_names(self):
        return [x.tag for x in self.get_leaves()]

    def find_depth_of_a_node(self, node):
        return self.tree.depth(node)

    def find_depth_of_a_path(self, path):
        for x in self.tree.all_nodes():
            if x.identifier == path:
                return self.find_depth_of_a_node(x)
        return None

    def trace_ancestry_of_a_node(self, node):
        ancestry = [node]
        cur_node = node
        while self.tree.parent(cur_node.identifier):
            ancestry.append(self.tree.parent(cur_node.identifier))
            cur_node = self.tree.parent(cur_node.identifier)
        output = [n for n in reversed(ancestry)]
        return output

    def search_node_tags(self, q):
        return [x for x in self.get_nodes() if q == x.tag]

    def search_node_identifiers(self, q):
        return [x for x in self.get_nodes() if q == x.identifier]

    def is_node_in_node(self, n, containing_n):
        if n.identifier in containing_n.fpointer:
            return True
        return False

    def does_node_match_string(self, n, id_string):
        return n.identifier == id_string

    def find_string_in_node_tag(self, n, a_string):
        return a_string in n.tag

    def find_string_in_node_identifier(self, n, a_string):
        return a_string in n.identifier

    def find_nodes_in_node(self, n, all_nodes=[], recursive=False):
        all_nodes = all_nodes + n.fpointer
        if recursive:
            for x in n.fpointer:
                if not x.is_leaf():
                    self.find_nodes_in_node(x, all_nodes=all_nodes, recursive=recursive)
        return all_nodes

    def find_leaves_in_node(self, n, all_leaves, recursive=False):
        all_leaves = all_leaves + [x for x in n.fpointer if x.is_leaf()]
        if recursive:
            for x in n.fpointer:
                if not x.is_leaf():
                    self.find_leaves_in_node(x, all_leaves=all_leaves, recursive=recursive)
        return all_leaves

    def find_tag_at_depth(self, tag, depth):
        potential_matches = [x for x in self.search_node_tags(tag)]
        matches = [x for x in potential_matches if self.find_depth_of_a_node(x) == depth]
        return matches
