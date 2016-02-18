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
from uchicagoldr.walktree import FileWalkTree
from datetime import datetime


# === classes for 

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
        return matches
        
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

    def find_files_in_a_node(self, a_node):
        return a_node.leaves()
        
    def get_tree(self):
        return self.tree

    def validate(self):
        return NotImplemented

    def validate_files(self):
        return NotImplemented

    def explain_validation_result(self):
        return NotImplemented

class DataTransferObject(object):
    def __init__(self, filep, source_checksum, destination_checksum, completed, uncorrupted):
        self.filepath = filep
        self.source = source_checksum
        self.destination = destination_checksum
        self.moved = completed
        self.uncorrupted = uncorrupted

    def write_to_manifest(self, manifestfile):
        opened = open(manifestfile, 'a')
        opened.write("{}\t{}\t{}\t{}\t{}\n".format(self.filepath, self.source,
                                                   self.destination, self.moved,
                                                   self.uncorrupted))
        opened.close()
        
class Stager(FileProcessor):
    def __init__(self, directory, numfiles, stage_identifier, prefix, source_root, archive_directory):
        FileProcessor.__init__(self, directory, source_root)
        self.destination_root = archive_directory
        self.source_root = source_root
        self.numfiles = numfiles
        self.prefix = prefix
        self.staging_id = stage_identifier

    def validate(self):
        numfilesfound = len(self.get_tree().get_files())
        if numfilesfound == self.numfiles:
            return True
        else:
            return False

    def explain_validation_results(self):
        if len(self.get_tree().get_files()) != self.numfiles:
            return namedtuple("ldrerror","category message")("fatal", "You said there were {} files, but {} files were found. This is a mismatch: please correct and try again.".format(str(self.numfiles),str(len(self.get_tree().get_files()))))
        else:
            return True

    def new_staging_directory(self):
        stage_id = self.staging_id
        return join(self.destination_root, stage_id)

    def new_staging_data_directory(self, stageID):
        return join(self.destination_root, stageID, 'data')

    def new_staging_admin_directory(self, stageID):
        return join(self.destination_root, stageID, 'admin')

    def new_staging_data_with_prefix(self, stageID):
        data_directories = sorted(listdir(join(self.destination_root, stageID, 'data')))
        last_number = len(data_directories)
        new_number = str(last_number + 1)
        return join(self.destination_root, stageID, 'data', self.prefix+new_number)

    def new_staging_admin_with_prefix(self, stageID):
        admin_directories = sorted(listdir(join(self.destination_root, stageID, 'admin')))
        last_number = len(admin_directories)
        new_number = str(last_number + 1)
        return join(self.destination_root, stageID, 'admin', self.prefix+new_number)        
    
    def make_a_directory(self, directory_string):
        if not exists(directory_string):
            try:
                mkdir(directory_string, 0o740)
                return "done"
            except IOError:
                return "invalid"
        else:
            return "already" 

    def select_manifest_file(self, admin_directory):
        manifest_file = join(admin_directory, 'manifest.txt')
        if exists(manifest_file):
            pass
        else:
            opened_file = open(manifest_file, 'w')
            opened_file.write("filepath\torigin(md5)\tstaging(md5)\torigin==staging\twas moved\n")
            opened_file.close()
            
        return manifest_file
        
    def setup_fresh_staging_environment(self):
        staging_directory = self.new_staging_directory()
        stageID = staging_directory.split('/')[-1]
        staging_data = self.new_staging_data_directory(stageID)
        staging_admin = self.new_staging_admin_directory(stageID)

        self.make_a_directory(staging_directory)
        self.make_a_directory(staging_data)
        self.make_a_directory(staging_admin)
        current_data_dir = self.new_staging_data_with_prefix(stageID)
        current_admin_dir = self.new_staging_admin_with_prefix(stageID)        
        self.make_a_directory(current_data_dir)
        self.make_a_directory(current_admin_dir)
        manifestwriter = self.select_manifest_file(current_admin_dir)
        return (current_data_dir, current_admin_dir, manifestwriter)

    def add_to_a_staging_environment(self):
        staging_directory = join(self.destination_root, self.staging_id)
        stageID = self.staging_id
        past_data_dirs = sorted(listdir(join(staging_directory, 'data')))
        last_data_dir_number = past_data_dirs[-1].split(self.prefix)[1]
        new_data_dir_number = int(last_data_dir_number) + 1
        new_data_dir_with_prefix = self.prefix+str(new_data_dir_number)
        current_data_dir = join(staging_directory, 'data', new_data_dir_with_prefix)
        current_admin_dir = join(staging_directory, 'admin', new_data_dir_with_prefix)
        self.make_a_directory(current_data_dir)
        self.make_a_directory(current_admin_dir)
        manifestwriter = self.select_manifest_file(current_admin_dir)
        return (current_data_dir, current_admin_dir, manifestwriter)

    def pickup_half_completed_staging_run(self):
        staging_directory = join(self.destination_root, self.staging_id)
        past_data_dirs = sorted(listdir(join(staging_directory, 'data')))
        last_data_dir_number = self.prefix + str(past_data_dirs[-1].split(self.prefix)[1])
        current_data_dir = join(staging_directory, 'data', last_data_dir_number)
        current_admin_dir = join(staging_directory, 'admin', last_data_dir_number)
        manifestwriter = self.select_manifest_file(current_admin_dir)
        return (current_data_dir, current_admin_dir, manifestwriter)


    def get_files_to_ingest(self, admin_dir):
        files = self.find_all_files()
        manifestfile = open(join(admin_dir, 'manifest.txt'),'r')
        manifestlines = manifestfile.readlines()
        manifestfiles = [x.split('\t') for x in manifestlines]
        manifestfiles = [x[0] for x in manifestfiles]
        new_files_to_ingest = [x for x in files if relpath(x.data.filepath, self.source_root) not in manifestfiles]
        return new_files_to_ingest

    def compare_source_to_origin(source, destination):
        destination_md5 = self.get_checksum(destination_file)
        source_md5 = self.get_checksum(source_file)
        if destination_md5 == source_md5:
            return True
        return False

    def ingest(self, ignore_mismatched_checksums = False,
               resume_partially_completed_run = False):
        
        def copy_source_directory_tree_to_destination(filepath):
            destination_directories = dirname(filepath).split('/')
            if filepath[0] == '/':
                directory_tree = "/"
            else:
                directory_tree = ""
            for directory_part in destination_directories:
                directory_tree = join(directory_tree, directory_part)
                if not exists(directory_tree):
                    mkdir(directory_tree, 0o740)

        if self.validate():
            if not exists(join(self.destination_root, self.staging_id)):
                current_data_directory, current_admin_directory, manifestwriter = \
                self.setup_fresh_staging_environment()
                files_to_ingest = self.get_files_to_ingest(current_admin_directory)
            elif resume_partially_completed_run:
                current_data_directory, current_admin_directory, manifestwriter = \
                self.pickup_half_completed_staging_run()
                files_to_ingest = self.get_files_to_ingest(current_admin_directory)
            else:
                current_data_directory, current_admin_directory, manifestwriter = \
                self.add_to_a_staging_environment()
                files_to_ingest = self.get_files_to_ingest(current_admin_directory)
        else:
            problem = self.explain_validation_result()
            stderr.write("{}: {}\n".format(problem.category, problem.message))
            _exit(2)

        for n in files_to_ingest:
            source_file = n.data.filepath
            destination_file = join(current_data_directory,
                                    relpath(n.data.filepath, self.source_root))
            
            copy_source_directory_tree_to_destination(destination_file)
            copyfile(source_file, destination_file)
            manifest_filepath = relpath(n.data.filepath, self.source_root)
            try:
                destination_md5 = self.get_checksum(destination_file)
                source_md5 = self.get_checksum(source_file)
                if destination_md5 == source_md5:
                    data_object = DataTransferObject(manifest_filepath,
                                              source_md5, destination_md5,'Y','Y')
                else:
                    data_object = DataTransferObject(manifest_filepath,
                                              source_md5, destination_md5, 'N','Y')
                    if ignore_mismatched_checksums:
                        pass
                    else:
                        raise IOError("{} destination file had checksum {}". \
                                      format(destination_file, destination_md5) + \
                                      " and source checksum {}".format(source_md5))   
            except:
                data_object = DataTransferObject(manifest_filepath,"null","null","null","Y")
            data_object.write_to_manifest(manifestwriter)
                
class Archiver(FileProcessor):

    """
    attributes: arkid, accnum, prefix, numfolders, numfiles, source_directory_root, archive_directory

    methods: validate, explain_validation_results, validate_files, ingest
    """    
    def __init__(self, directory, prefix, numfolders, numfiles,
                 source_root, archive_directory, group_id, user_id):

        FileProcessor.__init__(self, directory, source_root, irrelevant_part = source_root)
        self.prefix = prefix
        self.numfolders = numfolders
        self.numfiles = numfiles
        self.source_root = source_root
        self.destination_root = archive_directory
        self.destination_group = group_id
        self.destination_owner = user_id
        
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
                return namedtuple("ldererror", "category message")("fatal", "the following foldesr in admin did not have a complete set of fixity files: {}".format(','.join([x.identifier for x in find_fixity_files_in_admin])))
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
                try:
                    chown(destination_file, self.destination_owner, self.destination_group)
                except Exception as e:
                    stderr.write("{}\n".format(str(e)))
                destination_md5 = self.get_checksum(destination_file)
                if not destination_md5 == md5_checksum:
                    manifestfile = open(join(destination_file, 'manifest.csv','a'))
                    manifestwriter = writer(manifestfile, delimiter=",",quoting=QUOTE_ALL)
                    manifestwriter.writerow([destination_file, destination_md5, source_md5, 'N', 'Y'])
                    manifestfile.close()                    
                    if flag:
                        pass
                    else:
                        raise IOError("{} destination file had checksum {}".format(destination_file, destination_checksum) + \
                                      " and source checksum {}".format(md5_checksum))
                else:
                    manifestfile = open(join(destination_file, 'manifest.csv','a'))
                    manifestwriter = writer(manifestfile, delimiter=",",quoting=QUOTE_ALL)
                    manifestwriter.writerow([destination_file, destination_md5, source_md5, 'Y', 'Y'])
                    manifestfile.close()
        else:
            problem = self.explain_validation_result()
            stderr.write("{}: {}\n".format(problem.category, problem.message))

class NewArchiver(FileProcessor):
    def __init__(self, directory, prefix, numfolders, numfiles,
                 source_root, archive_directory, group_id, user_id):

        FileProcessor.__init__(self, directory, source_root, irrelevant_part = source_root)
        self.prefix = prefix
        self.numfolders = numfolders
        self.numfiles = numfiles
        self.source_root = source_root
        self.destination_root = archive_directory
        self.destination_group = group_id
        self.destination_owner = user_id

    def validate(self):
        admin_node = self.find_subdirectory_at_particular_level_down('admin',3)
        data_node = self.find_subdirectory_at_particular_level_down('data', 3)
        
        valid_admin = False
        for n in admin_node:
            current= admin_node.pop()
            subdirs_in_current = self.find_directories_in_a_directory(current)
            if len(subdirs_in_current) == self.numfolders:
                valid_admin = True
                
                premis_records = [x for x in subdirs_in_current if self.find_files_in_a_subdirectory(x, '*.premis.xml')]
                for premis_record in premis_records:
                    print(premis_record)
                    
        valid_data = False
        for n in data_node:
            current = data_node.pop()
            subdirs_in_current = self.find_directories_in_a_directory(current)
            if len(subdirs_in_current) == self.numfolders:
                valid_data = True
    
        return NotImplemented

    def explain_validation_results(self):
        admin_node = self.find_subdirectory_at_particular_level_down('admin', 3)
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

        return NotImplemented
    
    def ingest(self):
        if self.validate():
            return "good to ingest"
        else:
            self.explain_validation_results()
            return "it's invalid and here's why"
