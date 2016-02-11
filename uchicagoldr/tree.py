from collections import namedtuple
from hashlib import md5, sha256
from os import mkdir, stat
from os.path import abspath, dirname, exists, isdir, isfile, join, relpath
from magic import from_file
from shutil import copyfile
from treelib import Tree, Node
from uchicagoldr.filewalker import FileWalker
from uchicagoldr.moveableitem import MoveableItem

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
        self._derive_filemimetype()
        self._derive_checksums()

    def get_filepath(self):
        return self.filepath

    def get_filesize(self):
        return self.filesize

    def get_mimetype(self):
        return self.filemimetype

    def get_checksum_options(self):
        options = [key.split('checksum_')[1] for key in self.__dict__.keys() \
         if 'checksum' in key]
        return options

    def get_checksum(self, a_string):
        if getattr(self, "checksum_{}".format(a_string), None):
            return getattr(self, "checksum_{}".format(a_string), None)
        else:
            return False
    
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

    def _derive_checksums(self):
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
        self.checksum_md5 = md5_hash.hexdigest()
        self.checksum_sha256 = sha_hash.hexdigest()
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

class FileProcessor(object):
    """
    attributes: filewalker, tree

    methods: explain_nodes, find_matching_files_regex, find_matching_files, find_matching_subdirectories, get_tree, validate, validate_files, explain_validation_results
    """
    def __init__(self, directory, source_root, irrelevant_part = None):
        self.filewalker = FileWalker(directory)
        self.tree = FileWalkTree()

        for n in self.filewalker:
            self.tree.add_node(n, irrelevant_parts = irrelevant_part)

    def find_all_files(self):
        return self.get_tree().get_files()
            
    def find_directories_in_a_directory(self, a_node):
        current_level = a_node
        subdirectories = [self.find_matching_node(x) for x in current_level.fpointer if not self.find_matching_node(x).is_leaf()]
        return subdirectories
        
    def explain_nodes(self, a_list):
        return [namedtuple("node_explained", "id data")(n.identifier, n)
                for n in a_list]
        
    def pattern_matching_files_regex(self, regex):
        matches = [x for x in self.get_tree().get_all_nodes() if \
                   re_compile(regex).search(x.tag) and x.is_leaf()]
            
    def string_searching_files(self, val_string):
        matches =  [x for x in self.get_tree().get_files() if
                    self.get_tree().find_string_in_a_node_tag(x, val_string)]
        return matches
    
    def string_searching_subdirectories(self, val_string):
        matches = [x for x in self.get_tree().get_all_nodes() if
                   self.get_tree().is_it_a_subdirectory(x)]
        
        matches = [x for x in matches if self.get_tree(). \
                   find_string_in_a_node_tag(x, val_string)]
        return matches        

    def find_subdirectory_at_particular_level_down(self, val_string, level):
        level = int(level)
        potential_matches = self.string_searching_subdirectories(val_string)
        actual_matches = [x for x in potential_matches if self.get_tree().find_depth_of_a_node(x) == level]
        return actual_matches

    def find_matching_node(self, val_string):
        matches = [x for x in self.get_tree().get_all_nodes() if self.get_tree().does_node_match_string(x, val_string)]
        if len(matches) > 1:
            raise ValueError("too many matches for that identifier")
        elif len(matches) == 0:
            return False
        return matches[0]

    def get_checksum(self, filepath):
        blocksize = 65536
        md5_hash = md5()        
        file_run = open(filepath, 'rb')
        buf = file_run.read(blocksize)
        while len(buf) > 0:
            md5_hash.update(buf)
            buf = file_run.read(blocksize)
        file_run.close()
        return md5_hash.hexdigest()
    
    def find_file_in_a_subdirectory(self, a_node, file_name_string):
        node = self.find_matching_node(a_node.identifier)
        if len([x for x in node.fpointer if file_name_string in x]) == 1:
            return True
        return False
            
    def get_tree(self):
        return self.tree

    def validate(self):
        return NotImplemented

    def validate_files(self):
        return NotImplemented

    def explain_validation_result(self):
        return NotImplemented
    
class Stager(FileProcessor):

    """
    attributes: arkid, accnum, prefix, numfolders, numfiles, source_directory_root, archive_directory

    methods: validate, explain_validation_results, validate_files, ingest
    """
    
    
    def __init__(self, directory, prefix, numfolders, numfiles,
                 source_root, archive_directory):

        FileProcessor.__init__(self, directory, source_root, irrelevant_part = source_root)
        self.prefix = prefix
        self.numfolders = numfolders
        self.numfiles = numfiles
        self.source_root = source_root
        self.destination_root = archive_directory
        
    def validate(self):
        admin_node = self.find_subdirectory_at_particular_level_down('admin',3)
        data_node = self.find_subdirectory_at_particular_level_down('data', 3)
        
        if admin_node and data_node:
            subdirs_in_admin = self.find_directories_in_a_directory(admin_node.pop())
            subdirs_in_data = self.find_directories_in_a_directory(data_node.pop())
            if len(subdirs_in_data) == len(subdirs_in_admin) == self.numfolders:
                validate = True          
                for x in subdirs_in_admin:
                    find_fixity_files_in_admin = [x for x in subdirs_in_admin if 
                        self.find_file_in_a_subdirectory(x, 'fixityFromMedia.presform') and
                        self.find_file_in_a_subdirectory(x, 'fixityOnDisk.presform') and
                        self.find_file_in_a_subdirectory(x, 'rsyncFromMedia.presform')
                   ] 
                    if find_fixity_files_in_admin:
                        if len(subdirs_in_admin) == len(subdirs_in_data) == self.numfolders:
                            if self.numfiles == len(self.get_tree().get_files()):
                                return True
        return False
    
    def explain_validation_result(self):
        admin_node = self.find_subdirectory_at_particular_level_down('admin',3)
        data_node = self.find_subdirectory_at_particular_level_down('data', 3)
        if not admin_node:
            return namedtuple("ldrerror","category message")("fatal","missing \"admin\" folder in correct position in this directory")
        elif not data_node:
            return namedtuple("ldrerror","category message")("fatal","missing \"data\" folder in correct position in this directory")
        if admin_node and data_node:
            subdirs_in_admin = self.find_directories_in_a_directory(admin_node.pop())
            subdirs_in_data = self.find_directories_in_a_directory(data_node.pop())
            if len(subdirs_in_data) != len(subdirs_in_admin):
                return namedtuple("lderrror","category message")("fatal","subdirectories of data and admin are not equal in number")
            find_fixity_files_in_admin = [x for x in subdirs_in_admin if
                                          not self.find_file_in_a_subdirectory(x, 'fixityOnDisk.presform') or
                                          not self.find_file_in_a_subdirectory(x, 'fixityFromMedia.presform') or
                                          not self.find_file_in_a_subdirectory(x, 'mediaInfo.presform') or
                                          not self.find_file_in_a_subdirectory(x, 'rsyncFromMedia.presform')]
            if find_fixity_files_in_admin:
                return namedtuple("ldererror", "category message")("fatal", "the following foldesr in admin did not have a complete set of fixity files: {}".format(','.join(find_fixity_files_in_admin)))
        if len(self.get_tree().get_files()) != self.numfiles:
            return namedtuple("ldrerror", "category message")("fatal","There were {} files found in the directory, but you said there were supposed to be {} files".format(str(len(self.get_tree().get_files())),str(self.numfiles)))
        return True
    
    def validate_files(self):
        fixity_log_data = open(self.find_matching_files('fixityOnDisk.txt')[0], 'r').readlines() \
                          if self.find_matching_files('fixityOnDisk.txt') \
                             else None
        if not fixity_log_data:
            raise IOError("{} directory does not have a fixityOnDisk.txt file".format(self.filewalker.get_directory()))
        all_files = self.find_all_files()
        for x in all_files:
            line = [a for a in fixity_log_data if x.identifier in a]
            if line:
                fixity_log_checksum = line.split('\t')[0]
                if fixity_log_checksum == x.data.md5:
                    pass
                else:
                    raise IOError("{} had checksum {}".format(x.identifier, fixity_log_checksum) + \
                                   " in fixityOnDisk.txt file and checksum {}".format(x.data.md5) + \
                                  " in staging directory")
        return True

    def ingest(self, flag=False):
        def copy_source_directory_tree_to_destination(filepath):
            destination_directories = dirname(filepath).split('/')
            if filepath[0] == '/':
                directory_tree = "/"
            else:
                directory_tree = ""
            for directory_part in destination_directories:
                directory_tree = join(directory_tree, directory_part)
                if not exists(directory_tree):
                    mkdir(directory_tree, 0o750)
                    
        if self.validate():
            files_to_ingest = (n for n in self.find_all_files())
            for n in files_to_ingest:
                source_file = n.data.filepath
                md5_checksum = n.data.checksum_md5
                sha256_checksum = n.data.checksum_sha256
                file_size = n.data.filesize
                file_mimetype = n.data.filemimetype
                destination_file = join(self.destination_root,
                                        relpath(n.data.filepath, self.source_root))
                copy_source_directory_tree_to_destination(destination_file)
                copyfile(source_file, destination_file)
                destination_md5 = self.get_checksum(destination_file)
                if destination_md5 == md5_checksum:
                    print(n.data.filepath)
                else:
                    if flag:
                        pass
                    else:
                        raise IOError("{} destination file had checksum {}".format(destination_file, destination_checksum) + \
                                  " and source checksum {}".format(md5_checksum)) 
        else:
            return self.explain_validation_result()
