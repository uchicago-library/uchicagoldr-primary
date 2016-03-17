from os.path import join, split, isabs
from treelib import Tree, Node
from uchicagoldr.filewalker import FileWalker
from uchicagoldr.rootedpath import RootedPath

class FilePathTree(object):
    def __init__(self, path=None, filter_pattern=None):
        self.tree = Tree()
        if path:
            if not (isinstance(path, str) or isinstance(path, RootedPath)):
                raise ValueError()
            if isinstance(path, str):
                if not isabs(path):
                    raise ValueError()
            fw = FileWalker(path, filter_pattern=filter_pattern)
            for i, path in enumerate(fw):
                self.add_node(path)

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
