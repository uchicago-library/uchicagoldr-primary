
class FileWalker(object):
    items = []
    directory = None

    def __init__(self, directory_path, filter_pattern = None):
        self.directory = directory_path
        self.items = self.walk_directory(filter_pattern = filter_pattern)

    def __iter__(self):
        return self.items
        
    def walk_directory(self, filter_pattern = None,
                        directory = None):
        from os import listdir, walk
        from os.path import isdir, isfile, join
        from re import compile as re_compile
        if not directory:
            directory = self.directory
        flat_list = listdir(directory)
        while flat_list:
            node = flat_list.pop()
            fullpath = join(directory, node)
            if isfile(fullpath):
                if filter_pattern:
                    if re_compile(filter_pattern).search(fullpath):
                        yield fullpath
                    else:
                        pass
                else:
                    yield fullpath
            elif isdir(fullpath):
                for child in listdir(fullpath):
                    flat_list.append(join(fullpath, child))
        
class ADirectory(object):
    name = ""
    fullpath = ""
    a_type = ""

    def __init__(self, fullpath):
        self.name = fullpath
        self.fullpath = fullpath
        self.a_type = 'directory'

class AFile(object):
    name = ""
    fullpath = ""
    a_type = ""
    filesize = ""
    mimetype = ""
    checksum = ""

    def __init__(self, fullpath):
        self.name = fullpath
        self.fullpath = fullpath
        self.a_type = 'file'
        self.derive_mimetype()
        self.derive_filesize()
        self.derive_checksums()
        
    def derive_mimetype(self):
        def find_mimetype_from_extension():
            from mimetypes import guess_type
            return guess_type(self.filepath)[0]

        def find_mimetype_from_magic_number():
            from magic import from_file
            return from_file(self.fullpath, mime=True).decode("UTF-8")
        
        try:
            mimetype = find_mimetype_from_extension()

        except Exception as e:
            try:
                mimetype = find_mimetype_from_magic_number()
            except Exception as e:
                pass
        self.mimetype = mimetype

    def derive_filesize(self):
        from os import stat
        self.filesize = stat(self.fullpath).st_size

    def derive_checksums(self):
        from hashlib import sha256, md5
        blocksize = 65536
        afile = open(self.fullpath)
        buf = afile.read(blocksize)
        sha_hash = sha256()
        md5_hash = md5()
        while len(buf) > 0:
            sha_hash.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        self.sha256 = hash.hexdigest()
        afile = open(self.fullpath)
        buf = afile.blocksize(blocksize)
        while len(buf) > 0:
            md5_hash.update(buf)
            buf = afile.read(blocksize)
        afile.close()
        self.md5 = md5_hash.hexdigest()
    
class DirectoryTree(object):
    root = None
    filewalker = FileWalker
    
    def __init__(self, directory_path, filter_pattern = None):
        from os.path import dirname
        self.directory_path = directory_path
        self.filewalker = FileWalker(directory_path,
                                     filter_pattern = filter_pattern)

    def add_node(self, value):
        if not self.root:
            self.root = Node(value)
        else:
            current = self.root
        

    def find_node(self, value, current=None):
        if not current:
            current = self.root
        for n in current.nodes:
            print(n)
    
    # def search_for_a_node(a_string, node = None):
    #     if not current:
    #         current = self.root
    #     for n in self.nodes:
    #         if n.data.name == a_string:
    #             return n
    #         search_node(a_string, current = n)
    #     return False

    # def search_for_nodes(a_string, node = None):
    #     out = []
    #     if not current:
    #         current = self.root
    #     for n in self.nodes:
    #         if a_string in n.data.name:
    #             out.append(n)
    #         search_node(a_string, current = n)
    #     if out:
    #         return out
    #     else:
    #         return False

    # def add_a_node(self, a_string):
    #     if isdir(a_string):
    #         for n in a_string.split('/'):
    #             is_this_node_there = self.search_node(n)
    #             if is_this_node_there:
    #                 node_to_add_to = is_this_node_here
    #                 break
    #             print(n)
                
    #     elif isfile(a_string):
    #         new_file = AFile(a_string)
    #     else:
    #         raise TypeError("have to pass either a regular file or a directory to add a node to this tree")
        
    # def add_node(self, a_string):
    #     from os.path import isdir, isfile
    #     if not self.root:
    #         if isdir(a_string):
    #             a_directory = ADirectory(a_string)
    #             new_node = Node(a_directory)
    #             self.root = new_node
    #         else:
    #             raise TypeError("root node can't be a leaf")
    #     else:
    #         if isdir(a_string):
    #             self.root.find_directory(
    #         elif isfile(a_string):
    #             pass
    #         else:
    #                 raise TypeError("have to pass either a file or a directory that exists on disk")
    #         node_with_this_value = self.root.find_value(a_string)
    #         if node_with_this_value:
    #             return node_with_this_value
    #         else:
    #             pass

    
class Node(object):
    nodes = []
    data = None

    def __init__(self, data):
        self.data = data


    # def find_leaves(self):
    #     out = []
    #     for n in self.nodes:
    #         if n.data.data_type == 'file':
    #             out.append(n)
    #     return out

    # def find_directory(self):
    #     out = []
    #     for n in self.nodes:
    #         if n.data.data_type == 'directory':
    #             out.append(n)
    #         return out
    
    # def add_node(self,a_node):
    #     if isintance(a_node, Node):
    #         self.nodes.append(a_node)
    #     else:
    #         raise TypeError("must pass an instance of Node class")
