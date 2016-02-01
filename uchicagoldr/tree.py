


from hashlib import md5, sha256
from os import stat
from os.path import abspath, isdir, isfile, join
from magic import from_file
from treelib import Tree, Node
from uchicagoldr.filewalker import FileWalker

class LeafData(object):
    filepath = None
    filesize = None
    filemimetype = None
    filehchecksum = None

    def __init__(self, filepath):
        print(filepath)
        if filepath[0] != '/':
            self.filepath = abspath(filepath)
        else:
            self.filepath = filepath
        self.derive_filesize()
        self.derive_filemimetype()
        self.derive_checksums()
        
    def derive_filesize(self):
        from os import stat
        self.filesize = stat(self.filepath).st_size

    def derive_filemimetype(self):
        try:
            mimetype = guess_type(self.filepath)
        except Exception as e:
            mimetype = None
        try:
            mimetype = from_file(self.filepath, mime=True).decode('utf-8')
        except Exception as e:
            mimetype = None
        self.filemimetype = mimetype

    def derive_checksums(self):
        blocksize = 65536
        sha_hash = sha256()
        md5_hash = md5()
        
        file_run1 = open(self.filepath, 'rb')
        buf1 = file_run1.read(blocksize)
        while len(buf1) > 0:
            sha_hash.update(buf1)
            buf1 = file_run1.read(blocksize)
        file_run1.close()
        file_run2 = open(self.filepath, 'rb')
        buf2 = file_run2.read(blocksize)
        while len(buf2) > 0:
            md5_hash.update(buf2)
            buf2 = file_run2.read(blocksize)
        file_run2.close()
        self.md5 = md5_hash.hexdigest()
        self.sha256 = sha_hash.hexdigest()
        
            
class FileWalkTree(object):
    tree_root = None

    def __init_(self):
        self.tree_root = None

    def add_node(self, value):
        if not self.tree_root:
            self.tree_root = Tree()
            self.tree_root.create_node(value_parts[0],join('/',value_parts[0]))
            value_parts = value_parts[1:]
        parent = self.tree_root.root
        for position,value_part in enumerate(value_parts):
            if (position + 1) == len(value_parts):
                data = LeafData(join(parent, value_part))
                self.tree_root.create_node(value_part, join(parent,value_part), parent=parent,data=data)
            else:
                self.tree_root.create_node(value_part, join(parent,value_part), parent=parent)             
            parent = join(parent, value_part)

    def remove_node(self, value):
        return self.tree_root_remove_node(value)
        
    def find_node(self, id_value):
        
        return self.root.get_node(id_value)
    
