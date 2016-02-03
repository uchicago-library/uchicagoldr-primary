from hashlib import md5, sha256
from os import stat
from os.path import abspath, exists, isdir, isfile, join
from magic import from_file
from treelib import Tree, Node
from uchicagoldr.filewalker import FileWalker

class LeafData(object):
    """
    attributes: filepath, filesize, filemimetype, filechecksum

    methods: dervie_
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
            
class FileWalkTree(object):
    tree_root = None
    expanded_node_list = None
    def __init_(self):
        self.tree_root = None
        self.expanded_node_list = None
        
    def add_node(self, value):
        value_parts = value.split('/')[1:]
        if not self.tree_root:
            self.tree_root = Tree()
            self.tree_root.create_node(value_parts[0],join('/',value_parts[0])) 
        parent = self.tree_root.root
        for position,value_part in enumerate(value_parts[1:]):
            if position + 1 == len(value_parts[1:]):
                data = LeafData(join(parent, value_part))
                self.tree_root.create_node(value_part, join(parent,value_part), parent=parent,data=data)
                break
            
            elif self.tree_root.get_node(join(parent,value_part)):
                pass

            else:
                self.tree_root.create_node(value_part, join(parent,value_part), parent=parent)             
            parent = join(parent, value_part)

    def remove_node(self, value):
        self.tree_root.remove_node(value)
        return ""

    def get_all_nodes(self):
        self._expand_node_list()
        return self.expanded_node_list

    def _expand_node_list(self):
        if not self.expanded_node_list:
            self.expanded_node_list = self.tree_root.all_nodes()
        else:
            return False
        return True
    
    def __repr__(self):
        self.tree_root.show()
        return ""

class FileProcessor(object):

    def __init__(self, directory):
        self.filewalker = FileWalker(directory)
        self.tree = FileWalkTree()

        for n in self.filewalker:
            self.tree.add_node(n)

    def find_all_files(self):
        return [x for x in self.tree.tree_root.all_nodes() if x.is_leaf()]
        
    def find_matching_files_regex(self, regex):
        matches = [x for x in self.get_tree().get_all_nodes() if \
                   re_compile(regex).search(x.tag) and x.is_leaf()]
            
    def find_matching_files(self, val_string):
        matches = [x for x in self.get_tree().get_all_nodes() if \
                   val_string in x.tag and x.is_leaf()]
        return matches
        
    def find_matching_subdirectories(self, val_string):
        matches = [x for x in self.get_tree().get_all_nodes() if \
                   val_string in x.tag and not x.is_leaf()]
        return matches        

    def get_tree(self):
        return self.tree

    def validate(self):
        return NotImplemented

    def validate_files(self):
        return NotImplemented

    def explain_validation_result(self):
        return NotImplemented
    
class Stager(FileProcessor):
    arkid = None
    accnum = None
    prefix = None
    numfolders = None
    numfiles = None
    source_directory_root = None
    archive_directory = None
    
    def __init__(self, directory, eadnum, arkid, accnum, prefix,
                 numfolders, numfiles, source_root, archive_directory):
        FileProcessor.__init__(self, directory)
        self.eadnum = eadnum
        self.arkid = arkid
        self.accnum = accnum
        self.prefix = prefix
        self.numfolders = numfolders
        self.numfiles = numfiles
        self.source_root = source_root
        self.destination_root = archive_directory
        
    def validate(self):
        return len(self.find_matching_subdirectories('admin')) == 1 \
            and len(self.find_matching_subdirectories('data')) == 1 \
            and len(self.find_matching_subdirectories(self.eadnum)) == 1 \
            and len(self.find_matching_subdirectories(self.arkid)) == 1 \
            and len(self.find_matching_subdirectories(self.accnum)) == 1 \
            and len(self.find_matching_files('fixityFromOrigin.txt')) == 1 \
            and len(self.find_matching_files('fixityOnDisk.txt')) == 1 \
            and len(self.find_matching_subdirectories(self.prefix)) == self.numfolders \
            and len(self.find_all_files()) == self.numfiles

    def explain_validation_result(self):
        return NotImplemented
        
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

    def ingest(self):
        if self.validate():
            files_to_ingest = (n for n in self.find_all_files())
            for n in files_to_ingest:
                source_file = n.data.filepath
                md5_checksum = n.data.md5
                sha256_checksum = n.data.sha256
                file_size = n.data.filesize
                file_mimetype = n.data.filemimetype
                destination_file = join(self.destination_root,
                                        relpath(n.data.filepath, self.source_root))
                shutil.copyfile(source_file, destination_file)
                destination_md5 = self.get_checksum(destination_file)
                if destination_md5 == md5_checksum:
                    pass
                else:
                    raise IOError("{} destination file had checksum {}".format(destination_file, destination_checksum) + \
                                  " and source checksum {}".format(md5_checksum)) 
