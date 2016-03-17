from os.path import join, split
from treelib import Tree, Node
from uchicagoldr.filewalker import FileWalker

class FilePathTree(object):
    def __init__(self, fw):
        if not isinstance(fw, FileWalker):
            raise ValueError()
        self.tree = Tree()
        for i, path in enumerate(fw):
            if i == 0:
                if path[0] == '/':
                    self.tree.create_node("/", "/")
                else:
                    self.tree.create_node("", "")
            self._add_node(path)

    def _add_node(self, path):
        path_split = split(path)
        parent_path = path_split[0]
        leaf = path_split[1]
        if self.tree.get_node(path):
            return
        if not self.tree.get_node(parent_path):
            self._add_node(parent_path)
        self.tree.create_node(leaf, join(parent_path, leaf), parent=parent_path)
