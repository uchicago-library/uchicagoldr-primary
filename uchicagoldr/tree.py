from treelib import Tree, Node
from uchicagoldr.filewalker import FileWalker

class Stager(object):

    root_label = "root"
    def __init__(self, directory_path):
        self.filehandler = FileWalker(directory_path)
        tree = Tree()
        tree.create_node("Root","root")
        self.tree = tree

    def find_node(val):
        return NotImplemented
    
    def _adjust_file_path(self, filepath):
        return filepath.lstrip('/')

    def add_file_to_tree(self, file_string):
        NotImplemented
        file_string = self._adjust_filepath(file_string)
        file_parts = file_string.split('/')
        parent = root_label
        for fpart in file_string_parts:
            if dirtree.find_node(join(root,fpart)):
                # time to copy tree from the found-node down
                # add new stuff
                # merge new tree into old tree
                print(dirtree.find_node(join(root,fpart)).id)
    
            else:
                # node is new; just add that node in place
                dirtree.create_node(fpart,join(root,fpart),parent=root)
            parent = bulldup_path


        
    def update_tree(self, value)
        self.tree.get_node(value)
