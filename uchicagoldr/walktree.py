from collections import namedtuple
from csv import writer, QUOTE_ALL
from hashlib import md5, sha256
from os import _exit, chown, listdir, mkdir, stat
from os.path import abspath, dirname, exists, isdir, isfile, join, relpath
from magic import from_file
from pwd import getpwnam
from shutil import copyfile
from sys import stdout, stderr
from treelib import Tree, Node
from uchicagoldr.filewalker import FileWalker
from uchicagoldr.moveableitem import MoveableItem
from datetime import datetime


class LeafData(object):
    """
    == Attributes == 
    1. filepath
    2. filesize

    """

    def __init__(self, filepath):
        if not exists(filepath):
            raise IOError("{} directory must exist on disk.".format(filepath))
        if filepath[0] != '/':
            self.filepath = abspath(filepath)
        else:
            self.filepath = filepath
        self._derive_filesize()

    def get_filepath(self):
        """
        This function returns the value of the filepath attribute.
        """
        return self.filepath

    def get_filesize(self):
        """ 
        This function returns the value of the filesize attribute.
        """
        return self.filesize
    
    def _derive_filesize(self):
        """
        This function extracts the size of the file and sets it to the filesize attribute.
        """
        from os import stat
        self.filesize = stat(self.filepath).st_size

    def _derive_filemimetype(self):
        """
        This function extracts the mimetype of the file one of 2 ways: either from the 
        file extension or magic numbers but it prefers the magic numbers evaluation. It 
        then sets the filemimetype attribute.
        """
        try:
            mimetype = guess_type(self.filepath)
        except Exception as e:
            mimetype = None
        try:
            mimetype = from_file(self.filepath, mime=True).decode('utf-8')
        except Exception as e:
            mimetype = None
        self.filemimetype = mimetype

    def __repr__(self):
        return self.filepath 

class WalkTree(object):
    def __init__(self):
        self.tree_root = None
        self.expanded_node_list = None

    def add_node(self, value, sep="/"):
        value_parts = value.split(sep)[1:]
        if not self.tree_root:
            self.tree_root = Tree()
            self.tree_root.create_node(value_parts[0],join('/',value_parts[0])) 
        parent = self.tree_root.root
        for position, value_part in enumerate(value_parts)[1:]:
            self.tree_root.create_node(value_part, join(parent, value_part), parent=parent)

    def remove_node(self, value):
        self.tree_root.remove_node(value)

    def get_all_nodes(self):
        self._expand_node_list()
        return self.expanded_node_list

    def _expand_node_list(self):
        if not self.expanded_node_list:
            self.expanded_node_list = self.tree_root.all_nodes()
        else:
            return False
        return True

            
class FileWalkTree(WalkTree):
    """
    == Attributes ==
    1.  tree_root is the root of the tree 
    2. expanded_node_list is a flat list of every node in the tree
    """
    tree_root = None
    expanded_node_list = None
    def __init_(self):
        """
        This class gets initialized with an empty tree_root and an empty expanded node_list.
        """
        self.tree_root = None
        self.expanded_node_list = None
        
    def add_node(self, value, irrelevant_parts = None):
        """
        == Args ==
        1. value : literal string

        == KWArgs ==
        1. irrelevant_parts : literal string

        This function takes a string and builds a tree out of that literal string. If the irrelevant_parts string is included, the tree is build out of the value_parts minues the irrelelvant_parts string.
        """
        if not irrelevant_parts:
            value_parts = value.split('/')[1:]
        else:
            value_parts = value.split(irrelevant_parts)[1].split('/')
        if not self.tree_root:
            self.tree_root = Tree()
            self.tree_root.create_node(value_parts[0],join('/',value_parts[0])) 
        parent = self.tree_root.root
        for position, value_part in enumerate(value_parts[1:]):
            if position + 1 == len(value_parts[1:]):
                if irrelevant_parts:
                    data =  LeafData(irrelevant_parts+join(parent, value_part))
                else:
                    data = LeafData(join(parent, value_part))
                self.tree_root.create_node(value_part, join(parent,value_part), parent=parent,data=data)
                break
            
            elif self.tree_root.get_node(join(parent,value_part)):
                pass

            else:
                self.tree_root.create_node(value_part, join(parent,value_part), parent=parent)             
            parent = join(parent, value_part)
            
    def get_files(self):
        """
        This function returns all leaves in the tree.
        """
        return self.tree_root.leaves()

    def is_it_a_subdirectory(self, n):
        """
        == Paramters ==
        1. n : treelib.Node

        This function checks if a node n is a leaf and returns a boolean value.
        """
        return not n.is_leaf()

    def is_file_in_subdirectory(self, n, file_string):
        """
        == Args ==
        1. n : treelib.Node
        2. file_string : literal string
        
        Ths function returns a boolean asserting whether or not a leaf with the 
        string entered is immediately below the given node.
        """
        matches = [x for x in self.tree_root.get_node(n).fpointer \
                   if file_string in n.identifier]
        if matches:
            return True
        return False

    def find_file_contents_of_a_subdirectory(self, n, all_files=[]):
        """
        == Args ==
        1. n : treelib.Node

        == KWArgs ==
        1. all_files : list

        This function returns a list of leaves below the node.

        """
        matches = [x for x in self.tree.get_node(n).fpointer \
                   if self.tree.get_node(x).is_leaf()]
        
        for x in self.tree.get_node(n).fpointer:
            current = self.tree.get_node(x)
            if current.is_leaf():
                all_files.append(current)
            if not current.is_leaf():
                self.find_file_contents_of_a_subdirectory(x, all_files=all_files)
        return all_files
    
    def does_node_match_string(iself, n, id_string):
        """
        == Parameters ==
        1. n : treelib.Node
        2. id_string : literal string

        This function returns whether or not the node identifier matches the string.
        """
        return n.identifier == id_string
    
    def find_string_in_a_node_tag(self, n, a_string):
        """
        == Parameters == 
        1. n : treelib.Node
        2. a_string: literal_string

        This function checks if a string is in the tag name for a particular node 
        and returns either a boolean value or raises a TypeError

        """
        if isinstance(n, Node):
            return a_string in n.tag
        else:
            raise TypeError("must pass an object of type treelib.Node to the first parameter")

    def trace_ancestry_of_a_node(self, a_node):
        """
        == Parameters ==
        1. a_node : treelib.Node

        This function returns a list of identifiers tracing the given node to the root from
        left-to-right the root node to the node given.
        """
        ancestry = [a_node]
        while self.tree_root.parent(a_node.identifier):
            ancestry.append(self.tree_root.parent(a_node.identifier))
            a_node = self.tree_root.parent(a_node.identifier)
        output = [n for n in reversed(ancestry)]
        return output

    def find_depth_of_a_node(self, a_node):
        """
        == Parameters ==
        1. a_node : treelib.Node

        This function returns the depth level for a particular node as an integer.
        """
        return self.tree_root.depth(a_node)
    
    def __repr__(self):
        self.tree_root.show()
        return ""
