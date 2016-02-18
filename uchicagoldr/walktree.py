
from treelib import Tree, Node

class LeafData(object):
    """
    attributes: filepath, filesize, filemimetype, filechecksum

    methods: get_filepath, get_filesize, get_mimetype, get_checksum_options,
    get_checksum
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
        return self.filepath

    def get_filesize(self):
        return self.filesize
    
    def _derive_filesize(self):
        from os import stat
        self.filesize = stat(self.filepath).st_size

    def _derive_filemimetype(self):
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
    attributes: tree_root, expanded_node_list

    methods: add_node, remove_node, get_all_nodes, get_files, find_string_in_a_node_tag
    """
    tree_root = None
    expanded_node_list = None
    def __init_(self):
        self.tree_root = None
        self.expanded_node_list = None
        
    def add_node(self, value, irrelevant_parts = None):
        if not irrelevant_parts:
            value_parts = value.split('/')[1:]
        else:
            value_parts = value.split(irrelevant_parts)[1].split('/')
        if not self.tree_root:
            self.tree_root = Tree()
            self.tree_root.create_node(value_parts[0],join('/',value_parts[0])) 
        parent = self.tree_root.root
        for position,value_part in enumerate(value_parts[1:]):
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
        return self.tree_root.leaves()

    def is_it_a_subdirectory(self, n):
        return not n.is_leaf()

    def is_file_in_subdirectory(self, n, file_string):
        print(n)
        matches = [x for x in self.tree_root.get_node(n).fpointer \
                   if file_string in n.identifier]
        if matches:
            return True
        return False

    def find_file_contents_of_a_subdirectory(self, n, all_files=[]):
        matches = [x for x in self.tree.get_node(n).fpointer \
                   if self.tree.get_node(x).is_leaf()]
        
        for x in self.tree.get_node(n).fpointer:
            current = self.tree.get_node(x)
            if current.is_leaf():
                all_files.append(current)
            if not current.is_leaf():
                self.find_file_contents_of_a_subdirectory(x, all_files=all_files)
        return all_matches
    
    def does_node_match_string(iself, n, id_string):
        return n.identifier == id_string
    
    def find_string_in_a_node_tag(self, n, a_string):
        if isinstance(n, Node):
            return a_string in n.tag
        else:
            raise TypeError("must pass an object of type treelib.Node to the first parameter")

    def trace_ancestry_of_a_node(self, a_node):
        ancestry = [a_node]
        while self.tree_root.parent(a_node.identifier):
            ancestry.append(self.tree_root.parent(a_node.identifier))
            a_node = self.tree_root.parent(a_node.identifier)
        output = [n for n in reversed(ancestry)]
        return output

    def find_depth_of_a_node(self, a_node):
        return self.tree_root.depth(a_node)
    
    def __repr__(self):
        self.tree_root.show()
        return ""
